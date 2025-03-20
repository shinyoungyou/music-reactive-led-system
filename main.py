import pyaudio
import numpy as np
import RPi.GPIO as GPIO
import time
# Optional: 향후 Librosa를 이용한 고급 오디오 분석을 위해 임포트 (현재는 주석 처리)
# import librosa

# === GPIO 핀 설정 ===
# 시스템 다이어그램에 나온 핀 번호를 기반으로 LED 색상을 할당합니다.
LED_PINS = {
    'white': 24,
    'yellow': 23,
    'blue': 17,
    'red': 27,
    'green': 22
}

GPIO.setmode(GPIO.BCM)
for pin in LED_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# === PyAudio 설정 ===
CHUNK = 1024            # 오디오 프레임 당 샘플 수
FORMAT = pyaudio.paInt16  # 16비트 오디오
CHANNELS = 1            # 모노 오디오
RATE = 44100            # 샘플링 레이트 (Hz)

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# === LED 제어 함수 ===


def update_leds(volume):
    """
    오디오 볼륨에 따라 LED 패턴을 변경합니다.
    - 낮은 볼륨: 모든 LED 끄기
    - 중간 볼륨: 파란색 LED 켜기 (잔잔한 분위기)
    - 높은 볼륨: 노란색 또는 빨간색 LED 켜기 (강렬한 비트)
    """
    # 모든 LED를 일단 끕니다.
    for pin in LED_PINS.values():
        GPIO.output(pin, GPIO.LOW)

    # 볼륨에 따른 임계값 (튜닝 필요)
    if volume < 500:
        # 매우 낮은 볼륨: LED Off
        pass
    elif volume < 1500:
        # 중간 볼륨: 파란색 LED 켜기
        GPIO.output(LED_PINS['blue'], GPIO.HIGH)
    elif volume < 3000:
        # 볼륨이 좀 더 높으면: 노란색 LED 켜기
        GPIO.output(LED_PINS['yellow'], GPIO.HIGH)
    else:
        # 매우 높은 볼륨: 빨간색 LED 켜기
        GPIO.output(LED_PINS['red'], GPIO.HIGH)

    # 예시로, 특정 상황에 따라 초록색이나 흰색 LED를 추가적으로 사용할 수 있습니다.
    # 예: 비트가 감지되면 (Librosa 기반 비트 감지 추가 가능) 흰색 LED 점멸

# === (Optional) Librosa를 이용한 비트 감지 함수 ===
# 현재는 실시간 처리에 부담이 될 수 있으므로 기본 코드에서는 사용하지 않음.
# 필요 시, 버퍼링 후 librosa.onset.onset_detect()를 이용하여 비트를 감지하고 LED 제어에 반영할 수 있습니다.
#
# def detect_beat(audio_buffer):
#     # 오디오 버퍼를 float 형식으로 변환 (정규화)
#     y = audio_buffer.astype(np.float32) / 32768.0
#     onset_env = librosa.onset.onset_strength(y=y, sr=RATE)
#     if np.max(onset_env) > 1.0:  # 임계값 (튜닝 필요)
#         return True
#     return False


print("Music Reactive LED System 실행 중... (Ctrl+C로 종료)")

try:
    while True:
        # 마이크로부터 CHUNK 단위의 오디오 데이터 읽기
        data = stream.read(CHUNK, exception_on_overflow=False)
        # byte 데이터를 numpy 배열로 변환
        audio_data = np.frombuffer(data, dtype=np.int16)
        # RMS (Root Mean Square) 계산을 통해 볼륨 산출
        volume = np.sqrt(np.mean(audio_data**2))

        # 기본 볼륨 기반 LED 제어
        update_leds(volume)

        # Optional: 일정 버퍼를 모아 비트 감지 후 LED 패턴 변경
        # (추가 개발 시 구현)

        # 약간의 딜레이 (50ms)로 CPU 사용률 조절
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Music Reactive LED System 종료 중...")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    GPIO.cleanup()
