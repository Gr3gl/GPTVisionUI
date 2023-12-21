import openai as openai
import customtkinter as ctk
import base64

# Globals
global token_label
global token_slider
global gpt_textbox
global prompt_entry
global image_entry
global temperature_label
global temperature_slider
global base64_checkbox


# Generates an AI output from an image and prompt using GPT Vision
def generate_output(prompt, image_url, max_tokens, temperature):
    if base64_checkbox.get() == 1:
        base64_image = "temp"
        final_url = f"data:image/jpeg;base64,{base64_image}"
    else:
        final_url = image_url

    # TODO add checks if image link is selected, if there is a prompt

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": final_url,
                        },
                    },
                ],
            }
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

# Opens a window which has a textbox for the user to input their API Key
def open_api_window():
    dialog = ctk.CTkInputDialog(text="Please enter your OpenAI API Key \n(https://platform.openai.com/api-keys)", title="API Input")
    return dialog.get_input()

# Grabs OpenAI api key from a file
def get_api_key():
    with open('api_key.txt', 'a+') as key_file:  # Actually closes the file now
        key_file.seek(0) # seeks to start of file
        file_content = key_file.readline()
        if file_content != "": # Basic implementation of api_key guided setup
            return file_content
        else:
            api_input = open_api_window()
            key_file.write(api_input)
            return api_input


# Changes the token text to the value of the slider
def change_token_text(slider_value):
    token_string = "Tokens: {}".format(int(slider_value))
    token_label.configure(text=token_string)


# Changes the temperature text to the value of the slider
def change_temperature_text(slider_value):
    temperature_string = "Temperature: {}".format(round(slider_value, 2))
    temperature_label.configure(text=temperature_string)

def base_64_checked():
    if base64_checkbox.get() == 1:
        image_entry.configure(state="disabled")
    else:
        image_entry.configure(state="normal")

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


if __name__ == '__main__':
    first_run = True
    icon = "GPTVISION.ico"

    root = ctk.CTk()
    if first_run is True:
        client = openai.OpenAI(api_key=get_api_key())
        first_run = False

    # Window
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    root.geometry("720x700")
    root.title("GPT-4-Vision GUI")
    root.iconbitmap(icon)

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
    base64_checkbox = ctk.CTkCheckBox(master=frame, text="Base64 Local Image Upload (Drag and Drop)", command=base_64_checked, variable=check_var, onvalue=1, offvalue=0)
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

    root.mainloop()
