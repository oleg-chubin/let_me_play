/*jshint esversion: 6 */

import React, { Component } from 'react'
import PublicEvent from '../PublicEvent'

import './style.css'


class PublicTableau extends Component {
    constructor(props) {
        super(props);
        this.state = {trips: []};
    }

    async loadTrips() {
        this.setState({
            trips: await fetch(this.props.url, {credentials: 'include'}).then(response =>response.json())
        })
    }

    componentDidMount() {
        this.loadTrips();
        this.timerID = setInterval(
            () => this.tick(),
            60000
        );
    }

    componentWillUnmount() {
        clearInterval(this.timerID);
    }

    tick(){
        this.loadTrips();
    }

    render(){
        return(
            <div>
                {this.state.trips.map((item, index) => (
                    <PublicEvent item={item} />
                 ))}
            </div>
        );
    }
}

export default PublicTableau
