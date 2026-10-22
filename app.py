import os
import json
import random
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# The key is read automatically from the environment variable OPENAI_API_KEY
client = OpenAI()

TEXT_MODEL = os.environ.get("TEXT_MODEL", "gpt-4.1-mini")
IMAGE_MODEL = os.environ.get("IMAGE_MODEL", "gpt-image-1")

SETTINGS = [
    "a white cube gallery with polished concrete floors",
    "a museum vitrine under glass",
    "a lone plinth under a single spotlight",
    "a biennale pavilion with raw industrial walls",
]
LABEL_SYSTEM_PROMPT = """
You are the curatorial department of an imaginary contemporary art museum.
A visitor describes an ordinary object. You turn it into a work of art by writing
its wall label in "International Art English": abstract, inflated, deadpan.

RULES YOU ALWAYS FOLLOW:
1. STAY PRECISE ABOUT THE OBJECT. Name the real object and mention at least two true,
   concrete physical facts about it (material, colour, wear, size, use). Never invent
   features it does not have. The humour comes from the gap between the mundane object
   and the inflated language around it.
2. NOMINALIZE EVERYTHING. Prefer abstract nouns (-ity, -ality, -ization) and long
   noun chains: "proximity", "visibility", "the potentiality of withdrawal".
3. LET OBJECTS ACT. Use verbs like "interrogates", "problematizes", "articulates",
   "destabilizes", "stages", "forecloses". Avoid plain verbs like "is" or "has".
4. CITE EXACTLY ONE INVENTED THEORIST AND THEIR INVENTED BOOK inside the extended
   label, in the form: As [Name] argues in [Book Title]. Never use real names.
5. NEVER mention, imitate or quote real artists, critics, curators or theorists.
6. STAY DEADPAN. Never wink at the reader and never explain the joke.
7. The extended label must be ONE paragraph of between 80 and 120 words.
8. NEVER reuse the example phrases in this prompt. Invent a new bio, medium, provenance and credit line for every object, tied to that object.

TOMBSTONE FIELDS:
- artist: an invented name
- bio: one line in the form "b. [year], lives and works between [a real city] and [an absurd place]"
- title and year
- medium: the object's real materials mixed with one or two abstractions
- dimensions: in cm, realistic or absurdly monumental, or "Dimensions variable"
- provenance: a funny multi-step history of ownership, specific to this object
- credit_line: a "Gift of..." or "Courtesy of..." line tied to this object
- object: the plain, accurate name of the real object, used internally and never shown

Return ONLY a JSON object with exactly these keys:
artist, bio, title, year, medium, dimensions, provenance, credit_line, extended_label, object
"""

IMAGE_PROMPT_SYSTEM = """
You write prompts for an image generator. You will receive a museum wall label as JSON.
Write ONE paragraph (under 120 words) describing a documentary photograph of this
artwork installed in an exhibition.

RULES:
- Describe the object accurately, using the title, medium and extended label.
- The real object (see the "object" field) must stay clearly recognisable: keep its true shape, parts and function visible. Do not turn it into an abstract sculpture of something else.
- Use the DIMENSIONS to set the scale. If they are huge (e.g. 600 x 400 cm), the object
  fills the room and visitors look tiny. If they are small, it sits modestly on display.
  If they say "dimensions variable", show the work spreading or changing across the space.
- Use the curatorial setting you are given.
- Style: professional exhibition photography, soft gallery lighting.
- Never include a title card, caption or label in the picture.
Return only the prompt.
"""

def word_count(text):
    return len(text.split())


def make_label(description):
    """Step 1: write the museum label. Retry if the extended label has the wrong length."""
    label = {}
    for attempt in range(3):
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": LABEL_SYSTEM_PROMPT},
                {"role": "user", "content": f"Object: {description}"},
            ],
            response_format={"type": "json_object"},
            temperature=1.0,
        )
        label = json.loads(response.choices[0].message.content)
        if 80 <= word_count(label.get("extended_label", "")) <= 120:
            break
    return label

def make_image_prompt(label):
    """Step 2: write the image prompt FROM THE LABEL (not from the raw description)."""
    setting = random.choice(SETTINGS)
    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[
            {"role": "system", "content": IMAGE_PROMPT_SYSTEM},
            {"role": "user", "content": f"Curatorial setting: {setting}\n\nLabel:\n"
                                        + json.dumps(label, ensure_ascii=False)},
        ],
        temperature=0.7,
    )
    prompt = response.choices[0].message.content.strip()
    return prompt + " Absolutely no text, captions, wall labels, signage or lettering anywhere in the image."

    
def make_image(image_prompt):
    """Step 3: generate the image and return something a web page can display."""
    result = client.images.generate(model=IMAGE_MODEL, prompt=image_prompt, size="1024x1024")
    item = result.data[0]
    if getattr(item, "b64_json", None):
        return "data:image/png;base64," + item.b64_json   # base64 -> displayable
    return item.url


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    description = (data.get("description") or "").strip()[:300]
    if not description:
        return jsonify({"error": "Please describe an object."}), 400
    try:
        label = make_label(description)
        image_prompt = make_image_prompt(label)
        image_src = make_image(image_prompt)
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "The museum is closed for installation. Please try again."}), 500
    return jsonify({"label": label, "image_prompt": image_prompt, "image": image_src})


if __name__ == "__main__":
    app.run(debug=True)