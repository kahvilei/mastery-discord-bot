import React, { Component } from 'react';
import {summonerList} from '../assets/js/summonerData.js';
import Summoner from '../assets/js/SummonerWrapClass.js';

class Summoners extends Component{
      
    constructor() {
        super();
        this.state = { summoners: [] };
    }
    

    async componentDidMount() {
        var response = await summonerList();
        this.setState({ summoners: response });

    }

    render() {
        let summoner = new Summoner("FwbehkpR_zjpKu10OsPeJIXKJyy0grKEmdoZd0TvUVmx2ygWJk1056pUD1uEv7kyDsLaHF6EDkLlnw");
        <div>{summoner.name}</div>
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