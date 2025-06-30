import gradio as gr
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# بارگذاری مدل و توکنایزر
tokenizer = AutoTokenizer.from_pretrained("bolbolzaban/gpt2-persian")
model = AutoModelForCausalLM.from_pretrained("bolbolzaban/gpt2-persian")

# تابع تولید متن
def generate_text(prompt):
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output = model.generate(
        input_ids,
        max_new_tokens=120,
        do_sample=True,
        temperature=0.7,
        top_k=40,
        top_p=0.9,
        repetition_penalty=1.3,
        pad_token_id=tokenizer.eos_token_id
    )
    return tokenizer.decode(output[0], skip_special_tokens=True)

# رابط گرافیکی
gr.Interface(
    fn=generate_text,
    inputs=gr.Textbox(label="متن ورودی (پرامپت)", placeholder="مثلاً: در یک روز بهاری،"),
    outputs=gr.Textbox(label="متن تولید شده"),
    title="تولید متن فارسی با GPT2",
    description="مدل: bolbolzaban/gpt2-persian - تولید خودکار متن طبیعی به زبان فارسی"
).launch()
