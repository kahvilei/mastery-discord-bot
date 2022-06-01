import { summonerList } from '../assets/js/summonerData.js'
import React, { Component, Fragment } from 'react';
import ReactDOM from "react-dom";


class Summoners extends Component{
      
    constructor() {
        super();
        this.state = { summoners: [] };
    }
    

    async componentDidMount() {
        const response = await fetch("https://us-central1-summon-cloud.cloudfunctions.net/get_summoner_details?operation=get_all_summoners")
                               .then(response => response.json());
        const json = await response;
        this.setState({ summoners: json });

    }

    render() { 
        if(this.state.summoners){
            console.log(this.state.summoners)
            return(
            <section id="summoner-previews">
                <h2>Summoners</h2> 
                <div className="summoner-preview-list">
                    {this.state.summoners.map((data, key) => {
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
        return <div>Loading...</div>;
    }
  }

export default Summoners;