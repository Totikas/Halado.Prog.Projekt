import ollama
import json
import os


class fajl_ertelmezo:
    def __init__(self, log_utvonal: str, promt_utvonal: str, model_neve: str, kiiras_utvonal: str = 'elemzes_eredmeny.json'):
       self.log_utvonal = log_utvonal
       self.promt_utvonal = promt_utvonal
       self.model_neve = model_neve
       self.kiiras_utvonal = kiiras_utvonal

    def fajl_darabolas(self, sorok_szama=50, atfedes=5):

        darabok = []

        with open(self.log_utvonal, 'r', encoding='utf-8') as f:
            sorok = []

            for sor in f:
                sorok.append(sor.rstrip('\n'))

                if len(sorok) >= sorok_szama:
                    darabok.append(sorok.copy())
                    sorok = sorok[-atfedes:] if atfedes else []

            if sorok:
                darabok.append(sorok)

        return darabok

    
    def ai_elemzes(self, szoveg):

        valasz = ollama.chat(
            model=self.model_neve,
            messages=[
                {
                    'role': 'system',
                    'content': self.fajl_beolvasas(self.promt_utvonal)
                },
                {
                    'role': 'user',
                    'content': (
                        'Elemezd ezt a logfile-részletet. '
                        'Kizárólag az ebben a részletben található '
                        'bizonyítékokat használd.\n\n'
                        + szoveg
                    )
                }
            ],
            format='json',
            options={
                'temperature': 0,
                'num_ctx': 8192,
                'num_predict': 2048
            }
        )

        return json.loads(valasz.message.content)

    # fájlból beolvasás kezelás
    def fajl_beolvasas(self, adatok):
        try:        
            with open(adatok, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print('Hiba: A fájl nem található!')
            return None
        except Exception as e:
            print('Hiba történt a fájl beolvasásánál.')
            return None

    def json_mentes(self, valaszadas: str):

        try:
            tiszta_json_szoveg = valaszadas.strip()
        
            adat_json = json.loads(tiszta_json_szoveg)
                
            # Kiírjuk/elmentjük egy fájlba
            output_fajl = 'elemzes_eredmeny.json'
            with open(output_fajl, 'w', encoding='utf-8') as f:
                    json.dump(adat_json, f, ensure_ascii=False, indent=4)
                    
            print(f"\nAz eredmény sikeresen elmentve ide: {output_fajl}")
        except json.JSONDecodeError:
                print("\nHiba: Az AI válasza nem volt tiszta, érvényes JSON formátumú!")
                print("AI nyers válasza volt:", valaszadas)

   
    def futtatas(self):

        darabok = self.fajl_darabolas(
            sorok_szama=50,
            atfedes=5
        )

        osszes_incident = []

        print(f"Összesen {len(darabok)} részlet feldolgozása...")

        for index, darab in enumerate(darabok, start=1):

            print(f"\n[{index}/{len(darabok)}] Elemzés folyamatban...")

            szoveg = "\n".join(darab)

            try:
                eredmeny = self.ai_elemzes(szoveg)

                incidensek = eredmeny.get('incidents', [])

                osszes_incident.extend(incidensek)

                print(f"Talált incidensek: {len(incidensek)}")

            except Exception as e:
                print(f"Hiba a(z) {index}. rész feldolgozásánál: {e}")

        # Duplikalt incidensek kiszurese
        egyedi_incidentek = []
        latott = set()

        for incident in osszes_incident:

            kulcs = json.dumps(
                incident,
                sort_keys=True,
                ensure_ascii=False
            )

            if kulcs not in latott:
                latott.add(kulcs)
                egyedi_incidentek.append(incident)

        # Vegso JSON osszeallitasa
        vegso_eredmeny = {
            "summary": {
                "total_chunks": len(darabok),
                "suspicious_events_found": len(egyedi_incidentek)
            },
            "incidents": egyedi_incidentek
        }

        self.json_mentes(
            json.dumps(vegso_eredmeny, ensure_ascii=False)
        )



if __name__ == "__main__":
    AiLogertelmezo = fajl_ertelmezo(
        log_utvonal='webserver_security_test.log',
        promt_utvonal='ai_kezdopromt.txt',
        model_neve='qwen2.5:7b'
    )

    AiLogertelmezo.futtatas()
    