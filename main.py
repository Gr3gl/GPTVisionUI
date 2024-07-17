from openai import OpenAI
import customtkinter as ctk
from base64 import b64encode
from tkinterdnd2 import DND_FILES, TkinterDnD


# UI Globals
global token_label
global token_slider
global gpt_textbox
global prompt_entry
global image_entry
global temperature_label
global temperature_slider
global base64_checkbox
global output_list
global image_label


# Function to encode the image (From OpenAI)
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return b64encode(image_file.read()).decode('utf-8')


# Generates an AI output from an image and prompt using GPT Vision
def generate_output(prompt, image_source, max_tokens, temperature):
    if base64_checkbox.get() == 1:
        base64_image = encode_image(image_source)
        final_source = f"data:image/jpeg;base64,{base64_image}"
    else:
        final_source = image_source


    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": final_source,
                        },
                    },
                ],
            }
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    gpt_output = response.choices[0].message.content
    print(gpt_output)
    output_list.append(gpt_output)
    return gpt_output


# Opens a window which has a textbox for the user to input their API Key
def open_api_window():
    dialog = ctk.CTkInputDialog(text="Please enter your OpenAI API Key \n(https://platform.openai.com/api-keys)", title="API Input")
    return dialog.get_input()


# Grabs OpenAI api key from a file
def get_api_key():
    with open('api_key.txt', 'a+') as key_file:  # Actually closes the file now
        key_file.seek(0)  # seeks to start of file
        file_content = key_file.readline()
        if file_content != "":  # Basic implementation of api_key guided setup
            print("Successfully Read API Key")
            return file_content
        else:
            api_input = open_api_window()
            key_file.write(api_input)
            print("Wrote API Key to file api_key.txt")
            return api_input


# Changes the token text to the value of the slider
def change_token_text(slider_value):
    token_string = "Tokens: {}".format(int(slider_value))
    token_label.configure(text=token_string)


# Changes the temperature text to the value of the slider
def change_temperature_text(slider_value):
    temperature_string = "Temperature: {}".format(round(slider_value, 2))
    temperature_label.configure(text=temperature_string)


# Event which occurs when the base64 checkbox is checked
def base_64_checked():
    if base64_checkbox.get() == 1:
        image_entry.configure(state="normal", fg_color="#202020", text_color="#338dd4")  # I'll keep the state on normal instead of disabled incase you want to input a filepath
        image_label.configure(text="Enter Image Filepath or Drag and Drop Image:")
    else:
        image_entry.configure(state="normal", fg_color="#343738", text_color="#e6e6e6")  # e6e6e6 is my best guess
        image_label.configure(text="Enter Image URL:")


# Calls a prompt generation and edits the gpt_textbox
def generate_pressed():
    prompt = prompt_entry.get("0.0", "end")
    image_url = image_entry.get()
    tokens = int(token_slider.get())
    temperature = round(temperature_slider.get(), 2)
    result = generate_output(prompt, image_url, tokens, temperature)

    # textbox shit
    gpt_textbox.configure(state="normal")
    gpt_textbox.delete("0.0", "end")
    gpt_textbox.insert("0.0", result)
    gpt_textbox.configure(state="disabled")


# Event which is called when a file is drag and dropped onto the window
def drop(event):
    files = event.data
    if files:
        # Remove {} from file (if it has a space)
        files = str(files).replace("{", "").replace("}", "")
        print(f"File dropped: {files}")

        # Sets the filepath in the image_entry URL
        image_entry.delete(0, "end")
        image_entry.insert(0, files)

        # Checks the base64 box if it is not checked already
        if base64_checkbox.get() == 0:
            base64_checkbox.select()
            base_64_checked()


# Writes the GPT Generated Outputs to a file named output_log.txt
def write_output():
    with open('output_log.txt', 'w') as output_file:
        for output in output_list:
            output_file.write(output + '\n')


if __name__ == '__main__':
    # Definitions
    output_list = []

    # Window
    icon = "GPTVISION.ico"
    root = TkinterDnD.Tk()  # this change causes the title bar to become windows default color again (Maybe change in version 1.01)
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    root.geometry("720x700")
    root.title("GPT-4-Vision GUI")
    root.configure(background='#252525')
    root.iconbitmap(icon)
    root.resizable(False, False)  # Add resizability with a UI overhaul down the line if this picks up any traction at all (it wont)
    # These allow the window to register files that have been dropped on it using tkinterdnd2
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', drop)

    # Frame
    frame = ctk.CTkFrame(master=root)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Labels and entries
    prompt_label = ctk.CTkLabel(master=frame, text="Enter Prompt:")
    prompt_label.pack(anchor="w", padx=10, pady=6)

    prompt_entry = ctk.CTkTextbox(master=frame, width=680, height=70)
    prompt_entry.pack(anchor="w", padx=10)

    # Base 64 Checkbox
    check_var = ctk.StringVar(value="on")
    base64_checkbox = ctk.CTkCheckBox(master=frame, text="Base64 Local Image Upload", command=base_64_checked, variable=check_var, onvalue=1, offvalue=0)
    base64_checkbox.pack(anchor="w", padx=10, pady=4)

    image_label = ctk.CTkLabel(master=frame, text="Enter Image URL:")
    image_label.pack(anchor="w", padx=10, pady=2)

    image_entry = ctk.CTkEntry(master=frame, width=680)
    image_entry.pack(anchor="w", padx=10)

    token_label = ctk.CTkLabel(master=frame, text="Tokens: 100")
    token_label.pack(anchor="w", padx=10, pady=6)

    token_slider = ctk.CTkSlider(master=frame, from_=30, to=2000, number_of_steps=500, width=680, command=change_token_text)
    token_slider.pack(anchor="w", padx=10, pady=6)
    token_slider.set(100)

    # Temperature Slider
    temperature_label = ctk.CTkLabel(master=frame, text="Temperature: 0.3")
    temperature_label.pack(anchor="w", padx=10, pady=6)

    temperature_slider = ctk.CTkSlider(master=frame, from_=0, to=1, number_of_steps=100, width=680, command=change_temperature_text)
    temperature_slider.pack(anchor="w", padx=10, pady=6)
    temperature_slider.set(0.3)

    generate_button = ctk.CTkButton(master=frame, text="Generate", command=generate_pressed)
    generate_button.pack(anchor="w", padx=10, pady=8)

    gpt_textbox = ctk.CTkTextbox(master=frame, width=680, height=300, state="disabled")
    gpt_textbox.pack(anchor="w", padx=10, pady=9)

    client = OpenAI(api_key=get_api_key())

    root.mainloop()

    # Write the GPT Outputs to a file output_log.txt
    write_output()
