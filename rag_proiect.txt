import os
import re
from openai import OpenAI
import pdfplumber

# ================= CONFIGURARE FINALĂ =================
# Folosim exact structura găsită de tine:
AZURE_ENDPOINT = "https://YOUR-RESOURCE.services.ai.azure.com/openai/v1/"
API_KEY = "YOUR_AZURE_API_KEY" 
DEPLOYMENT_NAME = "Phi-4"
# ======================================================

client = OpenAI(
    base_url=AZURE_ENDPOINT,
    api_key=API_KEY,
)

def curata_text(text):
    """Curăță textul de caractere inutile"""
    text = re.sub(r'\s+', ' ', text) 
    return text.strip()

def citeste_si_fragmenteaza_pdfuri():
    """Citește PDF-urile și le împarte în pagini (chunks)"""
    baza_de_date = []
    fisiere_pdf = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not fisiere_pdf:
        print("⚠️ [EROARE] Nu am găsit niciun PDF!")
        return []
        
    print(f"\n[INFO] Am găsit {len(fisiere_pdf)} cursuri. Le indexez...")
    
    for nume_fisier in fisiere_pdf:
        try:
            print(f"  -> Indexez: {nume_fisier}...")
            with pdfplumber.open(nume_fisier) as pdf:
                for i, pagina in enumerate(pdf.pages):
                    text = pagina.extract_text()
                    if text:
                        fragment = {
                            "sursa": nume_fisier,
                            "pagina": i + 1,
                            "text": curata_text(text)
                        }
                        baza_de_date.append(fragment)
        except Exception as e:
            print(f"  [SKIPPED] Eroare la {nume_fisier}: {e}")

    print(f"[INFO] Gata! Am creat {len(baza_de_date)} fragmente de informație.\n")
    return baza_de_date

def gaseste_contexte_relevante(intrebare, baza_de_date, top_k=3):
    """Caută cele mai relevante 3 pagini"""
    cuvinte_cheie = set(intrebare.lower().split())
    
    scoruri = []
    for fragment in baza_de_date:
        text_fragment = fragment['text'].lower()
        scor = sum(1 for cuv in cuvinte_cheie if cuv in text_fragment)
        if scor > 0:
            scoruri.append((scor, fragment))
    
    scoruri.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scoruri[:top_k]]

def intreaba_phi4(intrebare, fragmente_relevante):
    print("\n[AI] Gândesc răspunsul...")
    
    context_text = ""
    for f in fragmente_relevante:
        context_text += f"\n--- Sursa: {f['sursa']} (Pagina {f['pagina']}) ---\n{f['text']}\n"
    
    if not context_text:
        return "Nu am găsit informații relevante în cursurile tale."

    prompt_final = f"""
    Folosește contextul de mai jos pentru a răspunde la întrebare.
    
    CONTEXT:
    {context_text}
    
    ÎNTREBARE:
    {intrebare}
    """

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "user", "content": prompt_final}
            ],
            temperature=0.1, # Mai precis, mai puține halucinații
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[EROARE] Azure API: {e}"

# ================= START =================
if __name__ == "__main__":
    db = citeste_si_fragmenteaza_pdfuri()
    
    if db:
        print("✅ Sistemul RAG este conectat corect la Phi-4!")
        print("-" * 60)
        
        while True:
            intrebare = input("\nÎntrebarea ta (sau 'exit'): ")
            if intrebare.lower() in ['exit', 'gata']:
                break
            
            # Căutăm doar paginile relevante (ca să nu depășim memoria)
            fragmente = gaseste_contexte_relevante(intrebare, db)
            
            if not fragmente:
                print("⚠️ Nu am găsit cuvinte cheie relevante în cursuri.")
                continue

            # Trimitem la AI
            raspuns = intreaba_phi4(intrebare, fragmente)
            print(f"\nRaspuns Phi-4:\n{'-'*60}\n{raspuns}\n{'-'*60}")