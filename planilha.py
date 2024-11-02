import requests
from bs4 import BeautifulSoup
import pandas as pd
from mutagen.mp3 import MP3

url = 'https://accent.gmu.edu/browse_language.php?function=find&language=portuguese'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Listas para armazenar os dados
speakers = []
birth_places = []
native_languages = []
other_languages = []
ages = []
sexes = []
english_onsets = []
learning_methods = []
english_residences = []
residence_lengths = []
audio_durations = []

# Encontrando todos os links de falantes portugueses
print("Buscando links de falantes...")
for link in soup.find_all('a'):
  href = link.get('href')
  if href and 'browse_language.php?function=detail&speakerid' in href:
    speaker_url = f'https://accent.gmu.edu/{href}'
    print(f"  - Acessando página do falante: {speaker_url}")
    speaker_response = requests.get(speaker_url)
    speaker_soup = BeautifulSoup(speaker_response.text, 'html.parser')

    # Extraindo dados biográficos
    bio_data = speaker_soup.find_all('ul', class_='bio')
    if bio_data:
      bio_items = bio_data[0].find_all('li')
      speaker = link.text.strip().replace(',', '') 
      birth_place = bio_items[0].text.split(':')[1].strip()
      
      if 'brazil' in birth_place: 
        print(f"    - Extraindo dados do falante: {speaker}")
        speakers.append(speaker)
        birth_places.append(birth_place)
        native_languages.append(bio_items[1].text.split(':')[1].strip())
        other_languages.append(bio_items[2].text.split(':')[1].strip())
        age_sex = bio_items[3].text.split(':')[1].strip().split(',')
        ages.append(int(age_sex[0])) 
        sexes.append(age_sex[1].strip())
        english_onsets.append(int(bio_items[4].text.split(':')[1].strip()))
        learning_methods.append(bio_items[5].text.split(':')[1].strip())
        english_residences.append(bio_items[6].text.split(':')[1].strip())
        residence_lengths.append(float(bio_items[7].text.split(':')[1].strip().split()[0]))

        # Extraindo a duração do áudio (corrigido)
        audio_source = speaker_soup.find('source', type='audio/mpeg')
        if audio_source:
          audio_url = f"https://accent.gmu.edu{audio_source['src']}"
          print(f"      - Baixando áudio: {audio_url}")
          audio_response = requests.get(audio_url)
          with open('temp_audio.mp3', 'wb') as f:
            f.write(audio_response.content)
          audio = MP3('temp_audio.mp3')
          duration = audio.info.length
          audio_durations.append(duration)
          print(f"      - Duração do áudio: {duration:.2f} segundos")

# Criando um DataFrame pandas
print("Criando DataFrame...")
df = pd.DataFrame({
  'Speaker': speakers,
  'Birth Place': birth_places,
  'Native Language': native_languages,
  'Other Languages': other_languages,
  'Age': ages,
  'Sex': sexes,
  'Age of English Onset': english_onsets,
  'English Learning Method': learning_methods,
  'English Residence': english_residences,
  'Length of English Residence (Years)': residence_lengths,
  'Audio Duration (seconds)': audio_durations
})

# Salvando o DataFrame em um arquivo Excel
print("Salvando dados em 'brazilian_speakers_data.xlsx'...")
df.to_excel('brazilian_speakers_data.xlsx', index=False)

print("Dados extraídos com sucesso!")