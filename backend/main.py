from downloader import download_audio
from analyzer import analyze_song
from prompt_generator import generate_prompt

url = input("YouTube URL 입력: ")

print("다운로드 중...")
path = download_audio(url)

print("곡 분석 중...")
result = analyze_song(path)

prompt = generate_prompt(result)

print("\n=== 분석 결과 ===\n")

print("BPM:", result["bpm"])
print("Key:", result["key"])

print("\nGenerated Prompt\n")
print(prompt)