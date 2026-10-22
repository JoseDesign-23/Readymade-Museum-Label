# Readymade: Museum Label Machine

Describe an everyday object and the app exhibits it as a work of contemporary art: an invented artist, a full museum tombstone, an extended wall label in "International Art English" (IAE), and an image of the object installed in a gallery.

**Live app:** https://readymade-museum-label.onrender.com

*(The site runs on a free plan, so the first visit after a quiet period can take about a minute to wake up.)*

![A miniature motorcycle (7 x 3 x 4 cm) on a plinth, with visitors leaning in](images/mini-motorcycle.png)


## 1. IAE features I chose and how I translated them into prompt rules

After reading Rule and Levine, I picked these features of IAE to exaggerate:

- Feature 1: Abstract nouns made from verbs: In the article, they explain how the IAE uses normal verbs and words and makes them a bit more fancy and intellectua, just so that the descriptiosn sound more academic. In the system prompt this became rule 2, which tells the model to prefer words like "proximity" and "visibility" and long chains of nouns.A granola bar ends up with "consumable materiality" and "metabolic potentiality"
- Feature 2: Objects that "act" with verbs like interrogates or problematizes: They also talk about how the object becomes more of a participant to the exhibition rather than just bening the object, by using verbs that make the object sound more like a subject. This became rule 3, which lists verbs such as "interrogates", "destabilizes" and "stages" and discourages plain verbs like "is". In my results, the labels are full of works that "problematize" and "interrogate" things.
- Feature 3:Authority borrowed from invented thinkers:The philosophical language of IAE was stated to be tahnks to some theorists in order to make the descriptions sound more academic and critical. This became rule 4: every label must cite one invented theorist and one invented book. Rule 5 forbids real names, so the machine borrows the style of authority without borrowing anyone's real reputation.

Other rules the machine always follows:

- Rule 1: stay precise about the object. The label must name the real object and mention true physical facts, so the humour comes from the gap between a mundane object and the inflated language.
- Rule 5: no real people. Real artists, critics and curators can never be named or quoted.
- Rule 6: stay deadpan. The machine never winks or explains the joke.
- Rule 7: length. The extended label must be one paragraph of 80 to 120 words. The code counts the words and asks again (up to three tries) if it is outside that range.
- Rule 8: no copied examples.** [Explain the problem you found: early labels reused my example bio and credit line word for word, so I added a rule and rewrote the tombstone instructions.]

I also made two changes in the code. The year is its own field because the title showed the year twice at first, and the generator randomly choosing a dimensions style for each object (realistic, monumental, miniature), so the scale rule is a bit more visible.


## 2. How the image prompt is derived from the label

The raw description is never sent to the image model. The pipeline is:

1. The model writes the label as JSON (artist, bio, title, year, medium, dimensions, provenance, credit line, extended label, and the plain name of the real object).
2. The code keeps only the **visual fields**: the object, title, medium and dimensions.
3. A second model call turns those fields into an image prompt. It uses the **dimensions** to set scale in words (a tiny object on a huge plinth, a work towering over the visitors) and picks one of four curatorial settings at random (white cube, vitrine, lone plinth under a spotlight, biennale pavilion).
4. The code adds a final instruction forbidding any text, captions or numbers in the image.
5. The image model generates the picture, and the page displays it next to the label.

Problems I found and fixed:

- First result was an abstract sculpture that barely looked like a motorcycle, did not have wheels or any sort of feature of a motorcycle. This was fixed with the label which includes the plain name of the object, and the image prompt must keep it recognisable.
- The generator was creating a label or caption right below the image that included name and size of the image. The fix was to send only the visual aspects and  numbers and names in the image prompt.

![A granola bar at realistic size](images/granola-bar.png)

![The same object as a giant granola bar: the label sets the scale](images/giant-granola-bar.png)


## 3. User guide

1. Open the live app.
2. Type the name of an object in the box (for example: a sports motorcycle or a green banana).
3. Press **Accession** and wait up to a minute.
4. The image appears on the left and the label on the right, like a gallery wall.
5. Try the same object more than once: the artist, the scale and the setting change each time.

![A sports motorcycle in the retro arcade interface](images/standard-motorcycle.png)

*Running it yourself:*

```
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
python app.py
```
Then open http://127.0.0.1:5000. The key is read from an environment variable and is never stored in the code.


## 4. Reflection: why is a language model so fluent in this dialect?

IAE is easy for a language model to imitate because it rebases itself on the repetitive vocabulary, predictable sentence  and recognizable patterns rather than very original expressions. As Rule and Levine explain, IAE frequently uses abstract words like visuality and potentiality, theoretical verbs and references to philosophical ideas to create an copy of the intellectual depth. Because language models learn to recognize and reproduce patterns in text, they can easily copy these conventions as well.

A language model has probably seen a lot of IAE, since this style of writing is used across many gallery websites, museum exhibition descriptions, artist statements, essays, art magazines and academic publications. Many of these texts are publicly available online and have similar vocabulary and sentence, so a model trained on large amounts of text can learn them.

As it was seen in the results form the prompt, the model would use that same rich vocabulary to describe mundane things such as the granola bar and the green banana. It became quite interesting when it came to generating the motorcycle nevertheless, maybe because of the complex nature of the piece itself. That type of language seemed natural. Another aspect was the fact that the model used also the specific words from the prompt since the example for it was right there.

IAE does not need to be true or specific to sound convincing. Its abstract language, complicated vocabulary and philosophical references can create a visual depth even when the meaning is vague. This suggests that IAE relies more on how something is expressed than on what is actually being communicated. That is why a model can write convincing art criticism without understanding anything, sounding sophisticated can be mistaken for having actual meaningful ideas.
