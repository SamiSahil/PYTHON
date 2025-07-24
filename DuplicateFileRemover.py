# Before you run this code, make sure to install this packages 
# pip install os
# pip install hashlib
# pip install tkinter


import os
import hashlib
from tkinter import filedialog, Tk, messagebox

def calculate_hash(filepath, block_size=65536):
    """
    Calculates the SHA256 hash of a file.
    
    This function reads the file in chunks to efficiently handle large files
    without loading the entire file into memory.
    
    Args:
        filepath (str): The path to the file.
        block_size (int): The size of the chunks to read from the file.
        
    Returns:
        str: The hexadecimal representation of the file's hash.
    """
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                sha256.update(data)
    except IOError:
        return None
    return sha256.hexdigest()

def find_duplicate_files(folder_path):
    """
    Finds duplicate files in a given folder and its subdirectories.
    
    This function walks through the directory tree, calculates the hash of each
    file, and stores them in a dictionary to identify duplicates.
    
    Args:
        folder_path (str): The path to the folder to scan.
        
    Returns:
        dict: A dictionary where keys are the hashes of duplicate files and
              values are lists of file paths that have that hash.
    """
    if not os.path.isdir(folder_path):
        messagebox.showerror("Error", "The selected path is not a valid directory.")
        return {}

    file_hashes = {}
    duplicates = {}

    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            
            # Skip empty files
            if os.path.getsize(file_path) > 0:
                file_hash = calculate_hash(file_path)
                
                if file_hash:
                    if file_hash in file_hashes:
                        # If the hash is already in our dictionary, it's a potential duplicate
                        if file_hash not in duplicates:
                            duplicates[file_hash] = [file_hashes[file_hash]]
                        duplicates[file_hash].append(file_path)
                    else:
                        file_hashes[file_hash] = file_path
                        
    return duplicates

def delete_duplicates(duplicates):
    """
    Deletes duplicate files, keeping one original copy of each file.
    
    This function iterates through the dictionary of duplicates and, for each set
    of duplicate files, it keeps the first one and deletes the rest.
    
    Args:
        duplicates (dict): A dictionary of duplicate files from find_duplicate_files.
        
    Returns:
        tuple: A tuple containing the number of deleted files and the total space saved.
    """
    deleted_count = 0
    space_saved = 0

    if not duplicates:
        messagebox.showinfo("No Duplicates Found", "No duplicate files were found in the selected folder.")
        return 0, 0

    for file_hash, file_paths in duplicates.items():
        # The first file in the list is considered the original and will be kept.
        # All other files with the same hash will be deleted.
        original_file = file_paths[0]
        
        for duplicate_file in file_paths[1:]:
            try:
                file_size = os.path.getsize(duplicate_file)
                os.remove(duplicate_file)
                deleted_count += 1
                space_saved += file_size
                print(f"Deleted: {duplicate_file}")
            except OSError as e:
                messagebox.showerror("Error", f"Error deleting file {duplicate_file}: {e}")

    return deleted_count, space_saved

def main():
    """
    The main function of the script.
    
    It initializes the GUI, prompts the user to select a folder, finds duplicates,
    and then asks for confirmation before deleting them. Finally, it shows a
    summary of the operation.
    """
    root = Tk()
    root.withdraw()  # Hide the main tkinter window

    folder_to_scan = filedialog.askdirectory(title="Select a folder to scan for duplicates")

    if folder_to_scan:
        print(f"Scanning for duplicate files in: {folder_to_scan}")
        
        duplicates_found = find_duplicate_files(folder_to_scan)

        if duplicates_found:
            total_duplicates = sum(len(files) - 1 for files in duplicates_found.values())
            
            confirmation_message = f"Found {total_duplicates} duplicate files.\n\n"
            confirmation_message += "The following files are duplicates and will be deleted:\n\n"

            for file_hash, file_paths in duplicates_found.items():
                 for file_path in file_paths[1:]:
                    confirmation_message += f"- {file_path}\n"
            
            confirmation_message += "\nDo you want to delete these files? One copy of each file will be kept."
            
            # Display the confirmation message in a scrollable text box
            confirm_window = Tk()
            confirm_window.title("Confirm Deletion")
            
            text_widget = Text(confirm_window, wrap='word', height=20, width=80)
            text_widget.pack(padx=10, pady=10)
            text_widget.insert('1.0', confirmation_message)
            text_widget.config(state='disabled')
            
            def on_confirm():
                confirm_window.destroy()
                deleted_count, space_saved_bytes = delete_duplicates(duplicates_found)
                space_saved_mb = space_saved_bytes / (1024 * 1024)
                
                summary_message = f"Operation complete!\n\n"
                summary_message += f"Deleted {deleted_count} duplicate files.\n"
                summary_message += f"Freed up {space_saved_mb:.2f} MB of space."
                
                messagebox.showinfo("Summary", summary_message)

            def on_cancel():
                confirm_window.destroy()
                messagebox.showinfo("Cancelled", "No files were deleted.")

            button_frame = Frame(confirm_window)
            button_frame.pack(pady=5)
            
            confirm_button = Button(button_frame, text="Delete Duplicates", command=on_confirm)
            confirm_button.pack(side='left', padx=10)
            
            cancel_button = Button(button_frame, text="Cancel", command=on_cancel)
            cancel_button.pack(side='left', padx=10)
            
            confirm_window.mainloop()

        else:
            messagebox.showinfo("No Duplicates Found", "No duplicate files were found in the selected folder.")
    else:
        messagebox.showinfo("Cancelled", "No folder was selected. The operation has been cancelled.")

if __name__ == "__main__":
    from tkinter import Text, Button, Frame
    main()
