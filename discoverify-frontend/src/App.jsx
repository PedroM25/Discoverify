import { useState, useEffect} from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [isVisible, setIsVisible] = useState(false);

  const handleClick = () => {
    setIsVisible(true);

    // Automatically hide the text after 2 seconds
    setTimeout(() => {
      setIsVisible(false);
    }, 2000); // Adjust this value to control how long the text stays visible before disappearing
  };

  return (
    <>
    <div className="App">
      <button onClick={handleClick} className="log-in-button">
        Log in to Spotify
      </button>
      {isVisible && <p>Successfully created </p>}
    </div>
    </>
  )
}

export default App
