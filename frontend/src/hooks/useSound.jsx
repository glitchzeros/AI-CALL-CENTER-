import React, { createContext, useContext, useState, useEffect } from 'react'
import { Howl } from 'howler'

const SoundContext = createContext()

export const useSound = () => {
  const context = useContext(SoundContext)
  if (!context) {
    throw new Error('useSound must be used within a SoundProvider')
  }
  return context
}

export const SoundProvider = ({ children }) => {
  const [soundEnabled, setSoundEnabled] = useState(true)
  const [sounds, setSounds] = useState({})

  useEffect(() => {
    // Load sound preferences from localStorage
    const savedPreference = localStorage.getItem('aetherium_sounds_enabled')
    if (savedPreference !== null) {
      setSoundEnabled(JSON.parse(savedPreference))
    }

    // Initialize sound objects
    const soundFiles = {
      paperSlide: '/sounds/paper-slide.mp3',
      penScratch: '/sounds/pen-scratch.mp3',
      paperUnfold: '/sounds/paper-unfold.mp3',
      bookClose: '/sounds/book-close.mp3',
      bellDing: '/sounds/bell-ding.mp3',
    }

    const loadedSounds = {}
    
    Object.entries(soundFiles).forEach(([key, src]) => {
      loadedSounds[key] = new Howl({
        src: [src],
        volume: 0.3,
        preload: true,
        onloaderror: () => {
          console.warn(`Failed to load sound: ${src}`)
        }
      })
    })

    setSounds(loadedSounds)
  }, [])

  const playSound = (soundName) => {
    if (!soundEnabled || !sounds[soundName]) return
    
    try {
      sounds[soundName].play()
    } catch (error) {
      console.warn(`Failed to play sound: ${soundName}`, error)
    }
  }

  const toggleSounds = () => {
    const newState = !soundEnabled
    setSoundEnabled(newState)
    localStorage.setItem('aetherium_sounds_enabled', JSON.stringify(newState))
  }

  // Specific sound functions for different actions
  const playPaperSlide = () => playSound('paperSlide')
  const playPenScratch = () => playSound('penScratch')
  const playPaperUnfold = () => playSound('paperUnfold')
  const playBookClose = () => playSound('bookClose')
  const playBellDing = () => playSound('bellDing')

  const value = {
    soundEnabled,
    toggleSounds,
    playSound,
    playPaperSlide,
    playPenScratch,
    playPaperUnfold,
    playBookClose,
    playBellDing,
  }

  return (
    <SoundContext.Provider value={value}>
      {children}
    </SoundContext.Provider>
  )
}