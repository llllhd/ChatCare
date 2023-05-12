import streamlit as st
from streamlit_chat import message
from inference import chat
from aip import AipSpeech
from audio_recorder_streamlit import audio_recorder
from scipy.io import wavfile
import numpy as np
from time import sleep

if 'gen' not in st.session_state:
    st.session_state['gen'] = []

if 'user' not in st.session_state:
    st.session_state['user'] = []

if 'temp' not in st.session_state:
    st.session_state['temp'] = ''

if 'tts_gen' not in st.session_state:
    st.session_state['tts_gen'] = []

if 'speech_client' not in st.session_state:
    APP_ID = '32036090'
    API_KEY = 'Sks9uoXZAfw7NSaA6nTY9eio'
    SECRET_KEY = 'GYceXIbjFx1HvUA2WSCSfGVQ9a0q54BE'
    st.session_state['speech_client'] = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

if 'keys' not in st.session_state:
    st.session_state['keys'] = 0

if 'audio_bytes' not in st.session_state:
    st.session_state['audio_bytes'] = None


def clear_input():
    st.session_state['temp'] = st.session_state['input']
    st.session_state['input'] = ''


def tts(text, id=None):
    try:
        result = st.session_state['speech_client'].synthesis(
            text,
            lang='zh',
            ctp=1,
            options={
                'per': 4,
                'spd': 5,
            }
        )
    except:
        result = None
    if isinstance(result, dict):
        result = None
    if id == None:
        return result
    else:
        st.session_state['tts_gen'][id] = result


def asr(audio_bytes):
    with open('audio.wav', 'wb') as f:
        f.write(audio_bytes)

    samplerate, data = wavfile.read('audio.wav')
    if data.ndim > 1:
        data = np.mean(data, axis=1, dtype=data.dtype)
    wavfile.write("audio.wav", samplerate, data)

    with open('audio.wav', 'rb') as f:
        speech = f.read()

    try:
        respoense = st.session_state['speech_client'].asr(
            speech=speech,
            format='wav',
            rate=16000
        )
        if respoense['err_msg'] != 'success.':
            return None
        else:
            return respoense['result'][0]
    except:
        return None


st.title('ChatCare')

st.text_input(' ', key='input', on_change=clear_input)

cols_asr = st.columns(9)
with cols_asr[4]:
    audio_bytes = audio_recorder(text='', icon_size='2x', sample_rate=16000)
if st.session_state['audio_bytes'] != audio_bytes:
    st.session_state['audio_bytes'] = audio_bytes
    audio_update = True
else:
    audio_update = False
if audio_update:
    st.session_state['temp'] = asr(audio_bytes=audio_bytes)
    if st.session_state['temp'] == None:
        st.error('语音识别发生了某些错误，请重试！', icon='🚨')
    if st.session_state['temp'] == '':
        st.warning('说话时间太短了，请重试！', icon='❗')


if st.session_state['temp']:
    with st.spinner('等待回复中...'):
        output = chat(
            st.session_state['temp'],
#             user=st.session_state['user'],
#             gen=st.session_state['gen'],
            temperature=0.7,
            # repetition_penalty=1
        )

    if output == 503:
        # st.info('ChatCare正在加载模型中，请稍等20秒左右重试...', icon='⏳')
        with st.spinner('⏳ChatCare正在加载模型中，请稍等...'):
            while chat('') in [503, None]:
                sleep(5)
        st.success('模型加载完成，开始聊天吧！', icon='🥳')

    elif output == None:
        st.error('发生了某些错误，请重试！', icon='🚨')

    else:
        st.session_state['user'].append(st.session_state['temp'])
        st.session_state['gen'].append(output)
        st.session_state['tts_gen'].append(tts(output))

    st.session_state['temp'] = ''


if st.session_state['gen']:
    for i in range(len(st.session_state['gen'])-1, -1, -1):

        message(st.session_state['gen'][i], key=f'gen_{i}')
        cols_audio_gen = st.columns(2)
        if st.session_state['tts_gen'][i] == None:
            cols_audio_gen[0].button(label='转语音失败，请点击重试', type='primary', on_click=tts, kwargs={
                                     'text': st.session_state['gen'][i], 'id': i}, key=st.session_state['keys'])
            st.session_state['keys'] += 1
        else:
            cols_audio_gen[0].audio(
                data=st.session_state['tts_gen'][i])

        message(st.session_state['user'][i],
                is_user=True, key=f'user_{i}')
