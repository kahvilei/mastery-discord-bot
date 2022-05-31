import logo from './logo.svg';
import './assets/css/App.css';
import Home from './pages/Home.js'
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  BrowserRouter
} from "react-router-dom";

function App() {
  return (

      <Router className="summoner-watcher-wrapper">
        <header className="summoner-watcher-header">
          <div id="header-content">
            <h1>Summoner Watch</h1>
            <nav>
                <Link to="/">Home</Link>
                <Link to="/leaderboards">Leaderboards</Link>
                <Link to="/summoners">Summoners</Link>
                <Link to="/experiments">Experiments</Link>
            </nav>
          </div>
        </header>
        <section id="main-content">
          <div id="main-content-wrap">
            <Routes>
                <Route path='/' element={<Home/>}/>
                <Route path='/leaderboards' element={<Leaderboards/>}/>
                <Route path='/summoners' element={<Summoners/>}/>
                <Route path='/experiments' element={<Experiments/>}/>
            </Routes>
          </div>
        </section>
        
      </Router>

  );
}


function Leaderboards() {
  return (
    <div>
      <h2>About</h2>
    </div>
  );
}

function Experiments() {
  return (
    <div>
      <h2>Dashboard</h2>
    </div>
  );
}

function Summoners() {
  return (
    <div>
      <h2>Dashboard</h2>
    </div>
  );
}

export default App;
