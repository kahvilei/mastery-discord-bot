import { liveData } from '../assets/js/liveData.js'
import {liveParticipantData} from '../assets/js/liveData.js'

function LiveMatches() {
    return (
        <section id="live-matches">
            <h2>Live Matches</h2> 
            <div className="live-match-preview-list">
                {liveData.map((data, key) => {
                return (
                    <div className="live-match-container" key={key}>
                        <div className = "summoner-icon"> 
                            <img src = {"http://ddragon.leagueoflegends.com/cdn/12.10.1/img/profileicon/" + data.profileIconId + ".png"}></img>
                        </div>
                        <div className = "summoner-info">
                            <h3 className = "summoner-name">
                                {data.name}
                            </h3>
                        </div>
                    </div>
                );
                })}
            </div>
        </section>
    );
  }

export default LiveMatches;