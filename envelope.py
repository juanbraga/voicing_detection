# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wav
import csv
import tradataset as td

def morph_close(audio, fs=44100, n=1024):
    
    result=np.zeros(np.size(audio))
    l=n/2+1  
    audio_abs=np.abs(audio)
    for i in range(l,len(audio)-l):
        result[i]=np.max(audio_abs[i-l:i+l])
    t = np.arange(len(result)) * (float(n)/fs)  
        
    return result, t, audio_abs
    
def set_threshold(fragment):
    
    silence_file = fragment + '_silence.wav'
    activity_file = fragment + '_activity.wav'
    
    fs, audio_silence = wav.read(silence_file)
    fs, audio_activity = wav.read(activity_file)        
    
    frame_size=512
    
    mc_silence, t_mc_silence, dummy = morph_close(audio_silence, fs, n=frame_size)  
    mc_activity, t_mc_activity, dummy = morph_close(audio_activity, fs, n=frame_size)
    
    plt.figure()
    plt.hist([mc_activity, mc_silence], bins = 200)
    plt.grid()
    plt.axis('tight')
    plt.show()
    
    var_activity = np.var(mc_activity)
    var_silence = np.var(mc_silence)
    
    return var_activity, var_silence
    

if __name__ == "__main__":
    
    dataset = td.load_list() 

    fragment = dataset[9]    
    
    audio_file = fragment + '_mono.wav'
    gt_file = fragment + '.csv'
    
    fs, audio = wav.read(audio_file)
    t = np.arange(len(audio)) * (1/float(fs))    
    
    audio_closed, t_mc, audio_abs = morph_close(audio, 4*880+1)
    
#    plt.figure(figsize=(18,6)) 
#    plt.plot(t_mc, audio_abs, 'r', label='wave')  
#    plt.plot(t_mc, audio_closed, 'k', label='envelope')
#    plt.grid()

    onset=[]
    notes=[]
    cr = csv.reader(open(gt_file,"rb"))
    for row in cr:
        onset.append(row[0]) 
        notes.append(row[1])
    onset = np.array(onset, 'float32')
    i=0
    aux_vad_gt = np.empty([0,], 'int8')
    for note in notes:
        if note=='0':
            aux_vad_gt = np.r_[aux_vad_gt,0]
        else:
            aux_vad_gt = np.r_[aux_vad_gt,1]
        i=i+1
    j=0
    vad_gt = np.empty([len(t),], 'int8')
    for i in range(1,len(onset)):
        while (j<len(t) and t[j]>=onset[i-1] and t[j]<=onset[i]):
            vad_gt[j]=aux_vad_gt[i-1]
            j=j+1     

#    plt.figure(figsize=(18,6))
#    plt.subplot(2,1,1)
#    plt.plot(t,audio)
#    plt.plot(t,(2**12)*vad_gt, label='VAD_gt')
#    plt.grid()
#    plt.title(fragment)
#    plt.tight_layout()
#    plt.subplot(2,1,2)
#    plt.plot(t_mc,audio_closed, label='envelope')
#    plt.plot(t,(2**12)*vad_gt, label='VAD_gt')
#    plt.grid()
#    plt.xlabel('Time (s)')
#    plt.legend(loc='best')
#    plt.tight_layout()
#    plt.show()
    
#%%
#    thershold_activity, thershold_silence = set_threshold(fragment)

    silence_file = fragment + '_silence.wav'
    activity_file = fragment + '_activity.wav'
    
    fs, audio_silence = wav.read(silence_file)
    fs, audio_activity = wav.read(activity_file)        
    
    frame_size=512
    
    mc_silence, t_mc_silence, dummy = morph_close(audio_silence, fs, n=frame_size)  
    mc_activity, t_mc_activity, dummy = morph_close(audio_activity, fs, n=frame_size)

    mean_activity = np.mean(mc_activity)
    mean_silence = np.mean(mc_silence)    
    stddev_activity = np.sqrt(np.var(mc_activity))
    stddev_silence = np.sqrt(np.var(mc_silence))
    
#%%
    plt.figure(figsize=(18,6))
    plt.hist([mc_activity, mc_silence], bins = 100)
    plt.grid()
    plt.axvline(mean_activity-stddev_activity, color='r', linestyle='dashed', linewidth=2)
    plt.axvline(mean_silence+stddev_silence, color='y', linestyle='dashed', linewidth=2)    
    plt.axis('tight')
    plt.show()

#%%
#    plt.figure(figsize=(18,6))
#    plt.subplot(2,1,1)
#    plt.plot(t,audio)
#    plt.plot(t,(2**12)*vad_gt, label='VAD_gt')
#    plt.grid()
#    plt.title(fragment)
#    plt.tight_layout()
#    plt.subplot(2,1,2)
#    plt.plot(t,audio_closed, label='envelope')
#    plt.plot(t,np.ones(len(t))*(mean_activity-stddev_activity),label='threshold')
#    plt.plot(t,(2**12)*vad_gt, label='VAD_gt')
#    plt.grid()
#    plt.xlabel('Time (s)')
#    plt.legend(loc='best')
#    plt.tight_layout()
#    plt.show()
    
#%% APPLY THRESHOLD
    
    thr=mean_activity-3.5*stddev_activity/4    
    aux = np.clip(audio_closed, 0, thr)
    aux[aux<thr] = 0
    aux = aux/thr
    plt.figure(figsize=(18,6))
    plt.plot(t,audio, color='black', alpha=0.3, label='Waveform')
    plt.fill_between(t, -(2**12)*aux,(2**12)*aux*0.5, facecolor='yellow', label='VAD', alpha=0.6)
    plt.fill_between(t, -(2**12)*vad_gt*0.5,(2**12)*vad_gt, facecolor='cyan', label='GT', alpha=0.6)
    plt.grid()
    plt.axis('tight')
    plt.legend(loc='lower right', fancybox=True, framealpha=0.5)
    plt.show()     
#    plt.savefig('docs/prueba.pdf', dpi=600)