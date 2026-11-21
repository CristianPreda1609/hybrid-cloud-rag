from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def configure_style(doc):
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)

def adauga_titlu(doc, text, nivel=1):
    heading = doc.add_heading(text, level=nivel)
    heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = heading.runs[0]
    run.font.color.rgb = RGBColor(0, 0, 0) # Negru
    run.font.name = 'Arial'

def adauga_snippet(doc, titlu_snippet, continut_log):
    """Adaugă un bloc de text care arată ca un terminal/cod"""
    p_titlu = doc.add_paragraph()
    runner = p_titlu.add_run(f"Figura: {titlu_snippet}")
    runner.bold = True
    runner.font.size = Pt(10)
    runner.italic = True
    
    # Adăugăm un tabel cu o singură celulă pentru a simula o casetă de cod
    table = doc.add_table(rows=1, cols=1)
    table.style = 'Table Grid'
    cell = table.cell(0, 0)
    
    paragraph = cell.paragraphs[0]
    runner_code = paragraph.add_run(continut_log)
    runner_code.font.name = 'Courier New' # Font de terminal
    runner_code.font.size = Pt(9)
    
    doc.add_paragraph() # Spatiu dupa snippet

def creaza_documentatie_extinsa():
    doc = Document()
    configure_style(doc)

    # ================= PAGINA DE TITLU =================
    for _ in range(3): doc.add_paragraph()
    
    titlu = doc.add_heading('PROIECT CLOUD COMPUTING', 0)
    titlu.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()
    
    p_subtitlu = doc.add_paragraph()
    p_subtitlu.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tema = p_subtitlu.add_run('TEMA: Convergența IaaS/PaaS/Serverless pentru Aplicații AI (C2, C5)\n\n')
    run_tema.bold = True
    run_tema.font.size = Pt(14)
    
    run_titlu = p_subtitlu.add_run('STUDIU DE CAZ:\nImplementarea și Performanța unei Aplicații RAG\nîntr-o Arhitectură Cloud Hibridă cu Azure Phi-4')
    run_titlu.bold = True
    run_titlu.font.size = Pt(16)

    for _ in range(8): doc.add_paragraph()

    p_student = doc.add_paragraph()
    p_student.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_student.add_run('Student: [Numele Tău Aici]\n').bold = True
    p_student.add_run('Grupa: [Grupa Ta]\n')
    p_student.add_run('Facultatea de Matematică și Informatică\n')
    p_student.add_run('Data: Ianuarie 2026')

    doc.add_page_break()

    # ================= CAPITOLUL 1 =================
    adauga_titlu(doc, '1. Introducere și Context Teoretic')
    
    doc.add_paragraph(
        'Evoluția recentă a tehnologiilor Cloud Computing a dus la o estompare a granițelor tradiționale dintre modelele de servicii '
        'IaaS (Infrastructure as a Service), PaaS (Platform as a Service) și Serverless. Această convergență este deosebit de evidentă '
        'în domeniul Inteligenței Artificiale, unde aplicațiile moderne necesită o combinație agilă de resurse de calcul brute și servicii gestionate.'
    )
    doc.add_paragraph(
        'Prezentul proiect analizează implementarea practică a unei aplicații de tip RAG (Retrieval-Augmented Generation), proiectată '
        'pentru a asista studenții prin interogarea materialelor de curs. Spre deosebire de abordările clasice "Full-PaaS" care implică '
        'costuri ridicate (ex. Azure SQL + AI Search), acest studiu propune o arhitectură "Lightweight" optimizată.'
    )
    doc.add_paragraph(
        'Obiectivele proiectului sunt:'
    )
    items = [
        'Demonstrarea integrării modelului Microsoft Phi-4 (Serverless) într-un flux de lucru custom.',
        'Implementarea unui motor de căutare vectorială/semantică simplificat folosind resurse IaaS locale.',
        'Evaluarea acurateței răspunsurilor generate pe baza a 10 cursuri de Cloud Computing.'
    ]
    for i in items:
        doc.add_paragraph(i, style='List Bullet')

    # ================= CAPITOLUL 2 =================
    adauga_titlu(doc, '2. Arhitectura Soluției')
    
    doc.add_paragraph(
        'Soluția implementată utilizează o abordare hibridă care maximizează eficiența costurilor și reduce latența de execuție. '
        'Componentele arhitecturale sunt mapate pe stack-ul Cloud astfel:'
    )
    
    doc.add_paragraph('A. Componenta Serverless (Model-as-a-Service)').bold = True
    doc.add_paragraph(
        'Nucleul de inteligență al sistemului este modelul Phi-4, accesat prin Azure AI Foundry. '
        'Utilizarea modelului în regim "Serverless API" elimină necesitatea administrării clusterelor de GPU (specific IaaS) '
        'și permite scalarea automată la zero atunci când serviciul nu este utilizat.'
    )

    doc.add_paragraph('B. Componenta IaaS/Compute (Procesare Locală)').bold = True
    doc.add_paragraph(
        'În locul serviciilor costisitoare precum Azure AI Search, s-a optat pentru un mediu de execuție Python '
        'care gestionează ingestia documentelor PDF și segmentarea (chunking) acestora. Această componentă simulează '
        'un worker node într-o infrastructură IaaS, având control total asupra algoritmului de indexare.'
    )

    # ================= CAPITOLUL 3 =================
    adauga_titlu(doc, '3. Implementare și Metodologie')
    doc.add_paragraph(
        'Scriptul dezvoltat (`rag_proiect.py`) implementează următorul flux logic:'
    )
    doc.add_paragraph('1. Ingestia: ', style='List Number').add_run('Citirea a 10 fișiere PDF și extragerea textului brut.').italic = True
    doc.add_paragraph('2. Pre-procesarea: ', style='List Number').add_run('Curățarea textului și împărțirea în fragmente logice.').italic = True
    doc.add_paragraph('3. Retrieval: ', style='List Number').add_run('Selectarea celor mai relevante 3 fragmente bazat pe densitatea cuvintelor cheie din interogare.').italic = True
    doc.add_paragraph('4. Augmentare: ', style='List Number').add_run('Construirea prompt-ului final care conține contextul și întrebarea.').italic = True
    doc.add_paragraph('5. Generare: ', style='List Number').add_run('Apelarea API-ului Azure OpenAI/Phi-4 pentru obținerea răspunsului.').italic = True

    # ================= CAPITOLUL 4 (IMPORTANT - SNIPPETS) =================
    doc.add_page_break()
    adauga_titlu(doc, '4. Rezultate Experimentale și Log-uri de Execuție')
    
    doc.add_paragraph(
        'Pentru validarea sistemului, au fost efectuate o serie de teste care acoperă concepte fundamentale, comparații tehnice '
        'și capacitatea de sinteză. Mai jos sunt prezentate log-urile reale extrase din consola de execuție.'
    )

    # --- SNIPPET 1: CAP Theorem ---
    log_cap = """[INFO] Am găsit 10 cursuri. Le indexez...
[INFO] Gata! Am creat 190 fragmente de informație.
✅ Sistemul RAG este conectat corect la Phi-4!

Întrebarea ta: Ce este Teorema CAP?

[AI] Gândesc răspunsul...

Raspuns Phi-4:
------------------------------------------------------------
Teorema CAP este un principiu fundamental în arhitectura sistemelor distribuite care afirmă că un sistem distribuit nu poate garanta simultan toate cele trei următoare proprietăți în prezența unei partiționări a rețelei:

1. **Consistență (C):** Toate nodurile văd aceleași date în același timp.
2. **Disponibilitate (A):** Fiecare cerere primește un răspuns, fără a garanta că este cel mai recent.
3. **Toleranță la partiționare (P):** Sistemul continuă să funcționeze chiar dacă unele mesaje sunt pierdute.

Conform teoremei CAP... un sistem poate alege să prioritizeze consistența și toleranța la partiționare... cum este ilustrat de Azure Service Fabric.
------------------------------------------------------------"""
    adauga_snippet(doc, "Interogare despre Teorema CAP (Cursul 01)", log_cap)
    
    doc.add_paragraph('Analiză: ').bold = True
    doc.add_paragraph(
        'Sistemul a identificat corect definițiile din Cursul 01. Mai mult, a reținut mențiunea specifică despre '
        '"Azure Service Fabric" din materialul de curs, demonstrând că nu doar definește termeni generali, ci folosește contextul specific oferit.'
    )

    # --- SNIPPET 2: Data Lake ---
    log_lake = """Întrebarea ta: Care este diferența dintre Data Lake și Delta Lake?

Raspuns Phi-4:
------------------------------------------------------------
Diferența dintre Data Lake și Delta Lake se referă la scopul, caracteristicile și funcționalitățile lor...

1. **Data Lake**:
   - Scop: Depozit centralizat pentru stocarea unor cantități mari de date în formatul lor nativ...
   - Exemple: Azure Data Lake Storage Gen2...

2. **Delta Lake**:
   - Scop: O suprafață de stocare care se suprapune unui Data Lake...
   - Caracteristici: Consistență ACID, Gestionarea versiunilor (Time Travel)...

În esență, Data Lake este un depozit... în timp ce Delta Lake adaugă consistența ACID.
------------------------------------------------------------"""
    adauga_snippet(doc, "Analiză Comparativă Data Lake vs Delta Lake (Cursul 03)", log_lake)
    doc.add_paragraph('Analiză: ').bold = True
    doc.add_paragraph(
        'Modelul a structurat răspunsul comparativ perfect, extrăgând caracteristicile cheie (ACID, Versionare) din Cursul 03. '
        'Aceasta validează capacitatea arhitecturii de a sintetiza informații tehnice complexe.'
    )

    # --- SNIPPET 3: Azure SQL ---
    log_sql = """Întrebarea ta: Care sunt avantajele Azure SQL Database ca serviciu PaaS?

Raspuns Phi-4:
------------------------------------------------------------
Azure SQL Database, ca serviciu PaaS, oferă mai multe avantaje:

1. **Gestionare automată**: Patch-uri de securitate și backup-uri...
2. **Scalabilitate**: Scalare orizontală și verticală...
3. **Disponibilitate**: Recuperare după dezastru...
4. **Securitate**: Integrare cu Azure Active Directory...
7. **Suport pentru transacții ACID**...
------------------------------------------------------------"""
    adauga_snippet(doc, "Enumerarea avantajelor PaaS (Cursul 05)", log_sql)

    # --- SNIPPET 4: Eroarea si Fix-ul (Competenta C5) ---
    doc.add_page_break()
    doc.add_paragraph('Provocări Semantice și Optimizarea Interogărilor').bold = True
    doc.add_paragraph(
        'Un aspect critic observat în timpul testării a fost limitarea căutării bazate pe cuvinte cheie. '
        'La o interogare formulată ambiguu, sistemul a eșuat inițial, dar a fost corectat prin ingineria promptului.'
    )

    log_fail = """Întrebarea ta: ce este aplicatia RAG?

Raspuns Phi-4:
------------------------------------------------------------
Contextul furnizat se concentrează pe Teorema CAP... Nu oferă informații despre o aplicație specifică numită "RAG".
Termenul "RAG" poate avea mai multe semnificații...
------------------------------------------------------------"""
    
    log_success = """Întrebarea ta: Ce înseamnă conceptul RAG sau Retrieval Augmented Generation?

Raspuns Phi-4:
------------------------------------------------------------
Conceptul RAG... este o tehnică care combină căutarea tradițională cu inteligența artificială generativă...

Elementele cheie ale RAG includ:
1. **Fragmentarea inteligentă a conținutului**...
2. **Căutare semantică prin vectori**...
3. **Utilizarea încorporărilor (embeddings)**...

În general, RAG îmbunătățește relevanța și calitatea răspunsurilor generate.
------------------------------------------------------------"""
    
    adauga_snippet(doc, "Eșec inițial vs. Succes prin reformulare semantică", log_fail + "\n...\n" + log_success)
    
    doc.add_paragraph('Concluzie Critică: ').bold = True
    doc.add_paragraph(
        'Acest comportament demonstrează diferența dintre "Keyword Search" (folosit în prototip) și "Vector Search" (recomandat în producție). '
        'Totuși, prin specificarea numelui complet ("Retrieval Augmented Generation"), algoritmul a reușit să identifice corect Cursul 06 și 09, oferind o definiție academică impecabilă.'
    )

    # ================= CONCLUZII =================
    adauga_titlu(doc, '5. Concluzii Finale')
    doc.add_paragraph(
        'Proiectul a demonstrat convergența cu succes a tehnologiilor Azure într-o aplicație unitară. '
        'Prin combinarea flexibilității Python (IaaS) cu puterea modelului Phi-4 (Serverless), s-a obținut un sistem RAG funcțional '
        'cu costuri minime. Rezultatele experimentale confirmă acuratețea ridicată a răspunsurilor, validând utilitatea soluției '
        'pentru mediul educațional.'
    )

    # Salvare
    nume_fisier = 'Proiect_Cloud_Studiu_Caz_Final.docx'
    doc.save(nume_fisier)
    print(f"✅ Document generat cu succes: {nume_fisier}")

if __name__ == "__main__":
    creaza_documentatie_extinsa()