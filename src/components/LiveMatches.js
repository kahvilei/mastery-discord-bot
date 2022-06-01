import { liveData } from '../assets/js/summonerData.js'

function LiveMatches() {
    return (
        <section id="live-matches">
            <h2>Live Matches</h2> 
            <div className="live-match-preview-list">
                {liveData.map((data, key) => {
                return (
                    <div className="live-match-container" key={data.gameId}>
                        <div className = "key-summoners">
                        {data.participants.map((data, key) => {   
                                if (data.isKey == true) {
                                        return (                   
                                            <div className="summoner-info" key={data.summonerName}>
                                                <div className = "summoner-icon"> 
                                                    <img src = {"http://ddragon.leagueoflegends.com/cdn/12.10.1/img/profileicon/" + data.profileIconId + ".png"}></img>
                                                </div>
                                                <div className = "summoner-info">
                                                    <h3 className = "summoner-name">
                                                        {data.summonerName}
                                                    </h3>
                                                </div>
                                            </div>
                                        );
                                }
                                })}
                        </div>
                        <div className = "all-participants">
                            <div className = "team1">
                                {data.participants.map((data, key) => {   
                                if (data.teamId == '100') {
                                        return (                   
                                            <div className="summoner-info" key={data.summonerName}>
                                                <div className = "summoner-icon"> 
                                                    <img src = {"http://ddragon.leagueoflegends.com/cdn/12.10.1/img/profileicon/" + data.profileIconId + ".png"}></img>
                                                </div>
                                                <div className = "summoner-info">
                                                    <p className = "summoner-name">
                                                        {data.summonerName}
                                                    </p>
                                                </div>
                                            </div>
                                        );
                                }
                                })}
                            </div>
                            <div className = "team2">
                                {data.participants.map((data, key) => {   
                                if (data.teamId == '200') {
                                        return (                   
                                            <div className="summoner-info" key={data.summonerName}>
                                                <div className = "summoner-icon"> 
                                                    <img src = {"http://ddragon.leagueoflegends.com/cdn/12.10.1/img/profileicon/" + data.profileIconId + ".png"}></img>
                                                </div>
                                                <div className = "summoner-info">
                                                    <p className = "summoner-name">
                                                        {data.summonerName}
                                                    </p>
                                                </div>
                                            </div>
                                        );
                                }
                                })}
                            </div>
                        </div>
                    </div>
                );
                })}
            </div>
        </section>
    );
  }

export default LiveMatches;