import os
import time
import re
import numpy as np
from openai import OpenAI
import pdfplumber

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ================= CONFIGURARE AZURE (Serverless Phi-4) =================
AZURE_ENDPOINT = "https://YOUR-RESOURCE.services.ai.azure.com/openai/v1/"
API_KEY = "YOUR_AZURE_API_KEY"
DEPLOYMENT_NAME = "Phi-4"

# ================= CONFIGURARE LOCALĂ (Embeddings) =================
MODEL_EMBEDDING_NAME = 'all-MiniLM-L6-v2' 

print(f"[INIT] Se încarcă modelul local de embeddings ({MODEL_EMBEDDING_NAME})...")
local_embedder = SentenceTransformer(MODEL_EMBEDDING_NAME)
print("[INIT] Model local încărcat cu succes!")

# Configurare client Azure
client = OpenAI(
    base_url=AZURE_ENDPOINT,
    api_key=API_KEY,
)

def curata_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def citeste_si_vectorizeaza_pdfuri():

    baza_de_date = []
    fisiere_pdf = [f for f in os.listdir('.') if f.endswith('.pdf')]

    if not fisiere_pdf:
        print("⚠️ [EROARE] Nu am găsit niciun PDF în folder!")
        return []

    print(f"\n[INFO] Am găsit {len(fisiere_pdf)} cursuri. Încep indexarea hibridă (Text + Vectori)...")

    total_pagini = 0
    for nume_fisier in fisiere_pdf:
        try:
            print(f" -> Procesez: {nume_fisier}...")
            with pdfplumber.open(nume_fisier) as pdf:
                for i, pagina in enumerate(pdf.pages):
                    text = pagina.extract_text()
                    if text:
                        text_curat = curata_text(text)
                        
                        vector = local_embedder.encode(text_curat)
                        
                        fragment = {
                            "sursa": nume_fisier,
                            "pagina": i + 1,
                            "text": text_curat,
                            "vector": vector 
                        }
                        baza_de_date.append(fragment)
                        total_pagini += 1
        except Exception as e:
            print(f" [SKIPPED] Eroare la {nume_fisier}: {e}")

    print(f"[INFO] Gata! Am indexat {total_pagini} pagini cu vectori semantici.\n")
    return baza_de_date

def cautare_hibrida(intrebare, baza_de_date, top_k=3):

    vector_intrebare = local_embedder.encode(intrebare).reshape(1, -1)
    
    cuvinte_cheie = set(intrebare.lower().split())
    
    scoruri_finale = []

    for fragment in baza_de_date:
        # A. Calcul Scor Semantic (Cosinus Similarity) - returnează valoare între 0 și 1
        # Reshape este necesar pentru că sklearn așteaptă matrice 2D
        vector_fragment = fragment['vector'].reshape(1, -1)
        scor_semantic = cosine_similarity(vector_intrebare, vector_fragment)
        
        # B. Calcul Scor Lexical (Cuvinte cheie)
        text_lower = fragment['text'].lower()
        match_count = sum(1 for cuv in cuvinte_cheie if cuv in text_lower)
        # Normalizăm scorul lexical (îl împărțim la lungimea întrebării pentru a nu domina)
        scor_lexical = match_count / len(cuvinte_cheie) if len(cuvinte_cheie) > 0 else 0
        
        # C. Scor Hibrid Ponderat
        # Dăm prioritate sensului (70%), dar validăm cu termeni exacti (30%)
        scor_final = (0.7 * scor_semantic) + (0.3 * scor_lexical)
        
        scoruri_finale.append((scor_final, fragment))

    # Sortăm descrescător după scorul final
    scoruri_finale.sort(key=lambda x: x, reverse=True)
    
    # Returnăm doar textele fragmentelor de top
    return [item[1] for item in scoruri_finale[:top_k]]

def intreaba_phi4(intrebare, fragmente_relevante):
    print("\n[AI] Trimit contextul către Azure Phi-4...")
    
    context_text = ""
    for f in fragmente_relevante:
        context_text += f"\n--- Sursă: {f['sursa']} (Pag. {f['pagina']}) ---\n{f['text'][:1500]}...\n"

    if not context_text:
        return "Nu am găsit informații relevante. Încearcă să reformulezi."

    prompt_final = f"""
    Ești un asistent universitar expert în Cloud Computing. Răspunde la întrebare folosind DOAR informațiile din contextul de mai jos.
    
    CONTEXT DIN CURSURI:
    {context_text}

    ÎNTREBARE STUDENT:
    {intrebare}
    """

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "Ești un asistent util care răspunde în limba română."},
                {"role": "user", "content": prompt_final}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        # Verificăm dacă răspunsul este obiect (Standard OpenAI v1)
        if hasattr(response, 'choices'):
            return response.choices[0].message.content
            
        # Verificăm dacă răspunsul este dicționar (Legacy/Compatibilitate)
        elif isinstance(response, dict):
            return response['choices']['message']['content']
            
        else:
            return f"Format răspuns necunoscut: {type(response)}"

    except Exception as e:
        return f"[EROARE] Azure API: {e}"
# ================= MAIN LOOP =================

if __name__ == "__main__":
    # Pasul 1: Indexare Hibridă (rulează o singură dată la pornire)
    db = citeste_si_vectorizeaza_pdfuri()

    if db:
        print(f"✅ Sistem Hibrid (Local Embeddings + Azure Phi-4) Inițializat!")
        print("-" * 60)

        while True:
            intrebare = input("\nÎntrebarea ta (sau 'exit'): ")
            if intrebare.lower() in ['exit', 'gata', 'quit']:
                break
            
            
            start_time = time.time()
            
            # Pasul 2: Retrieval Hibrid 
            fragmente = cautare_hibrida(intrebare, db)
            
            end_time = time.time()
            
            latenta_ms = (end_time - start_time) * 1000
            print(f"[METRICĂ] Latență Căutare: {latenta_ms:.2f} ms") 
            
            # -----------------------------------
            
            if not fragmente:
                print("⚠️ Nu am găsit documente relevante.")
                continue
            
            print(f"[DEBUG] Surse identificate:")
            for f in fragmente:
                print(f" - {f['sursa']} (p.{f['pagina']})")

            raspuns = intreaba_phi4(intrebare, fragmente)
            
            print(f"\nRăspuns Phi-4:\n{'-'*60}\n{raspuns}\n{'-'*60}")