import requests
import tkinter as tk
import webbrowser
import pygame  # Import pygame for background music

def open_url_from_position(event, text_widget):
    """Handle clicking on a URL from the text widget."""
    index = text_widget.index(tk.CURRENT)  # Get position where click happened
    line = text_widget.get(f"{index.split('.')[0]}.0", f"{index.split('.')[0]}.end")  # Get the entire line
    for word in line.split():
        if word.startswith("http"):
            webbrowser.open(word)  # Open the URL

def get_price_data(item_name, text_widget, filter_accessories):
    url = f"https://data.unwrangle.com/api/getter/?platform=amazon_search&search={item_name.replace(' ', '+')}&country_code=us&page=1&api_key=d5b91c77771beb4c62bc24ffdeec76751b80a993"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        if data["success"] and data["result_count"] > 0:
            results = data['results']
            
            # Filter out products that do not match the search term and exclude unwanted categories if specified
            exclusion_keywords = ['cable', 'controller', 'dock', 'charging'] if filter_accessories else []
            filtered_results = [
                result for result in results 
                if item_name.lower() in result['name'].lower() 
                and not any(keyword.lower() in result['name'].lower() for keyword in exclusion_keywords)
                and result.get('price') is not None  # Exclude listings with no price
            ]
            
            # If no relevant results, display a message
            if not filtered_results:
                text_widget.config(state=tk.NORMAL)
                text_widget.delete(1.0, tk.END)
                text_widget.insert(tk.END, f"❌ No relevant results found for '{item_name}'.")
                text_widget.config(state=tk.DISABLED)
                return
            
            # Sort filtered results by price (Low to High)
            filtered_results = sorted(filtered_results, key=lambda x: (x.get('price') is None, x.get('price') or float('inf')))
            
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, f"🔍 Found {len(filtered_results)} results for '{item_name}' (Sorted by Price - Low to High):\n\n")

            for idx, result in enumerate(filtered_results, 1):
                text_widget.insert(tk.END, f"📦 Product {idx}:\n", "title")
                text_widget.insert(tk.END, f"   🏷️ Name: {result['name']}\n", "bold")
                text_widget.insert(tk.END, f"   💲 Price: {result['currency_symbol']}{result['price']}\n", "bold")
                text_widget.insert(tk.END, f"   ⭐ Rating: {result['rating']} ({result['total_ratings']} ratings)\n")
                
                # Insert the URL as a clickable item
                text_widget.insert(tk.END, f"   🔗 URL: {result['url']}\n", "link")
                text_widget.insert(tk.END, f"   🚚 Shipping Info: {', '.join(result['shipping_info']) if result.get('shipping_info') else 'No shipping info available'}\n")
                
                more_buying_choices = result.get('more_buying_choices')
                if more_buying_choices and "offer_text" in more_buying_choices:
                    text_widget.insert(tk.END, f"   🔄 More Buying Choices: {more_buying_choices['offer_text']}\n")
                else:
                    text_widget.insert(tk.END, "   🔄 More Buying Choices: No offers available\n")

                text_widget.insert(tk.END, "-" * 70 + "\n", "separator")
            
            text_widget.config(state=tk.DISABLED)
        else:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, f"❌ No results found for '{item_name}'.")
            text_widget.config(state=tk.DISABLED)
    else:
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, f"⚠️ Failed to fetch data. Status Code: {response.status_code}")
        text_widget.config(state=tk.DISABLED)

def search():
    item_name = entry.get().strip()
    filter_accessories = filter_var.get()  # Get the state of the checkbox (True or False)
    if item_name:
        get_price_data(item_name, text_area, filter_accessories)

# Tkinter GUI setup
root = tk.Tk()
root.title("Amazon Price Scout")
root.geometry("900x600")
root.minsize(500, 400)

# Set the window icon
root.iconbitmap('assets/icon.ico')

# Initialize pygame for music
pygame.mixer.init()
pygame.mixer.music.load("assets/BGM.mp3")
pygame.mixer.music.set_volume(0.1)  # Set volume (0.0 to 1.0)
pygame.mixer.music.play(-1, 0.0)  # Loop the music indefinitely

# Styling
root.configure(bg="#f8f9fa")

frame = tk.Frame(root, bg="#f8f9fa")
frame.pack(pady=10)

tk.Label(frame, text="🔎 Enter Item Name:", font=("Arial", 12, "bold"), bg="#f8f9fa").grid(row=0, column=0, padx=5, pady=5)
entry = tk.Entry(frame, width=50, font=("Arial", 12))
entry.grid(row=0, column=1, padx=5, pady=5)

# Checkbox to filter accessories
filter_var = tk.BooleanVar(value=True)  # Default is True (filter accessories)
filter_checkbox = tk.Checkbutton(frame, text="Include Accessories", variable=filter_var, font=("Arial", 12, "bold"), bg="#f8f9fa")
filter_checkbox.grid(row=0, column=2, padx=5, pady=5)

tk.Button(frame, text="Search", command=search, font=("Arial", 12, "bold"), bg="#007bff", fg="white").grid(row=1, column=1, padx=5, pady=5)

# Resizable Text widget
text_area = tk.Text(root, width=70, height=25, wrap=tk.WORD, font=("Arial", 11))
text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

# Tag styles
text_area.tag_configure("title", font=("Arial", 12, "bold"), foreground="#0056b3")
text_area.tag_configure("bold", font=("Arial", 11, "bold"))
text_area.tag_configure("separator", foreground="#aaaaaa")
text_area.tag_configure("link", foreground="#007bff", underline=True)

# Bind click event for URL detection
text_area.bind("<Button-1>", lambda event: open_url_from_position(event, text_area))

root.mainloop()
