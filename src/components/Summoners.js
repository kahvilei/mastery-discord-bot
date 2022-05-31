import summonerData from '../assets/js/summonerData.js'

function Summoners() {
    var connector = new summonerData();
    var summonerList = connector.getAllSummoners();
    return (
        <section id="summoner-previews">
            <h2>Summoners</h2> 
            <div className="summoner-preview-list">
                {summonerList.map((data, key) => {
                return (
                    <div className="summoner-container" key={key}>
                        <div className = "summoner-icon"> 
                            <img src = {"http://ddragon.leagueoflegends.com/cdn/12.10.1/img/profileicon/" + data.profileIconId + ".png"}></img>
                        </div>
                        <div className = "summoner-info">
                            <h3 className = "summoner-name">
                                {data.name}
                            </h3>
                            <div className = "summoner-level">
                                Level {data.summonerLevel}
                            </div>
                        </div>
                    </div>
                );
                })}
            </div>
        </section>
    );
  }

export default Summoners;