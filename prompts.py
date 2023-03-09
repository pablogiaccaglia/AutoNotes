from enum import Enum


class Prompts(Enum):
    NLP_SLIDES = """write as a book paragraph what i'll provide to you. 
You need to explain the content i give to you, 
using as many words as possible, when needed use bullet points, 
but not overuse them, mix them with plain text. 
Keep in mind that this text needs to be used as a studying resource, so it must be as exhaustive as possible.  Write the answer in markdown, use titles and subtitles
The topic is Natural Language Processing, do not explain what NLP is.
Here's the query, remember to not explain what NLP is.: \n\n"""""

    BIOFISICA_SLIDES = """"scrivi un paragrafo di un libro con il testo che ti fornirò.
Devi spiegare il contenuto che ti fornirò, aggiungendo dettagli ed informazioni importanti per capire meglio, usando più parole possibile, se serve usa elenchi puntati, ma non ne usare troppi,
usali insieme a testo normale. Puoi usare termini inglesi se serve.
Ricordati che il testo generato deve essere usato per studiare, quindi deve essere il più esauistivo possibile.
Scrivi la risposta in markdown, usa titoli h1 e sottotitoli.
L'argomento è BIOFISICA CELLULARE E MOLECOLARE, non spiegare cosa è la BIOFISICA CELLULARE E MOLECOLARE

Ecco il testo, ricordati di non spiegare cos'è la BIOFISICA CELLULARE E MOLECOLARE. : \n\n"""