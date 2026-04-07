import gradio as gr
from router import stream_brochure


# Gradio Interface

view = gr.Interface(
    fn=stream_brochure,
    inputs=[
        gr.Textbox(label="Company Name"),
        gr.Textbox(label="Website URL"),
        gr.Dropdown(
            ["llama3.2", "gemini"],
            label="Select Model",
            value="llama3.2"
        ),
        gr.Textbox(
            label="Language (Default: English)",
            value="English"
        )
    ],
    outputs=gr.Markdown(label="Generated Brochure"),
    flagging_mode="never"
)


# Run App

if __name__ == "__main__":
    view.launch()
