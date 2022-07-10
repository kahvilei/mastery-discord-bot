import React, { Component } from 'react';
import SummonerList from '../assets/js/SummonerListClass.js';

class Leaderboard extends Component{
      
    constructor() {
        super();
        this.display = "Win rate";
        this.filter = "";
        this.state = { summoners: []};
    }
    

    async componentDidMount() {
        var summonerArray = await SummonerList.build(this.display, this.filter);
        console.log(summonerArray);
        this.setState({ summoners: summonerArray});
    }

    render() {
        var place = 0;
        if(this.state.summoners.list){
            return(
            <section id={this.display} className = "leaderboard">
                <h3>{this.display}</h3> 
                <div className="leaderboard-list">  
                    {this.state.summoners.list.map((summoner, key) => {
                    return (
                        <div className="summoner-container" key={key}>
                            <div className="name-and-place">
                            <div className = {"place" + place + " place"}>{place +=1}</div>
                            <div className = "summoner-icon"> 
                                <img src = {summoner.icon()}></img>
                            </div>                            
                            <h3 className = "summoner-name">
                                {summoner.name()}
                            </h3>
                            </div>
                            <div className = "summoner-stat">
                                {summoner.stat(this.display, this.filter)}
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

export default Leaderboard;