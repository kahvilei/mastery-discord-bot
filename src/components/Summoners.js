import React, { Component } from 'react';
import SummonerList from '../assets/js/SummonerListClass.js';

class Summoners extends Component{
      
    constructor() {
        super();
        this.state = { summoners: []};
    }
    

    async componentDidMount() {
        var summonerArray = await SummonerList.build();
        console.log(summonerArray);
        this.setState({ summoners: summonerArray});
    }

    render() {
        if(this.state.summoners.list){
            return(
            <section id="summoner-previews">
                <h2>Summoners</h2> 
                <div className="summoner-preview-list">
                    {this.state.summoners.list.map((summoner, key) => {
                    return (
                        <div className="summoner-container" key={key}>
                            <div className = "summoner-icon"> 
                                <img src = {summoner.icon()}></img>
                            </div>
                            <div className = "summoner-info">
                                <h3 className = "summoner-name">
                                    {summoner.name()}
                                </h3>
                                <div className = "summoner-level">
                                    Level {summoner.level()}
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