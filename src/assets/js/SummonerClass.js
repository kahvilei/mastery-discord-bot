//TODO summoner wrapper class that grabs data and performs calculations

class Summoner{
    constructor(data) {
        this.data = data;
    }

    name() {
        return this.data.name;
    }

    icon() {
        return "http://ddragon.leagueoflegends.com/cdn/12.10.1/img/profileicon/" + this.data.profileIconId + ".png";
    }

    level() {
        return parseInt(this.data.summonerLevel);
    }
}

export default Summoner;