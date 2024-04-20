import { useState, useEffect} from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [currentTime, setCurrentTime] = useState(0)

  useEffect(() => {
    fetch('http://localhost:5000/time').then(res => res.json()).then(data => {
      setCurrentTime(data.time);
    });
  });

  return (
    <>
      <button className="log-in-button">
        Log in to Spotify
      </button>
    </>
  )
}

export default App
