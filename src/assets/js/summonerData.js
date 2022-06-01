
const csummonerList =
    fetch("https://us-central1-summon-cloud.cloudfunctions.net/get_summoner_details?operation=get_all_summoners")
    .then(response => response.json());

export const summonerList = () =>
    new Promise((resolve, reject) => {
      setTimeout(
        () =>
        fetch("https://us-central1-summon-cloud.cloudfunctions.net/get_summoner_details?operation=get_all_summoners")
        .then(response => response.json()),
        Math.random() * 100
      );
});

const liveData = 'no';

