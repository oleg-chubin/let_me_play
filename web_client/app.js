/*jshint esversion: 6 */

import React from 'react'
import ReactDOM from 'react-dom'
import { PublicTableau } from './components'


var reiseplans = document.getElementsByClassName("event-tableau");
Object.keys(reiseplans).map(function(item, index){
    var apiurl = reiseplans[item].getAttribute('data-apiurl');
    ReactDOM.render(
        <PublicTableau url={apiurl} />,
        reiseplans[item]
    );
});
