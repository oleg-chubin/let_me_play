/*jshint esversion: 6 */

import React, { Component } from 'react'

import './style.css'

class PublicEvent extends Component {
    constructor(props) {
        super(props);
        this.state = {'cardState': 'normal'};
    }

    rotateCard(){
        var state = (this.state.cardState === "normal") ? "hover" : "normal";
        this.setState({"cardState": state});
    }

    render(){ return(
        <div className="col-md-4 col-sm-6" key={this.props.item.id}>
             <div className={this.state.cardState + ' card-container manual-flip'} key={this.props.item.id}>
                <div className="card" key={this.props.item.id}>

                    <div className="front">
                        <div className="cover">
                            <img src={this.props.item.court.image}/>
                        </div>
                        <div className="user">
                            <img className="img-circle" src={this.props.item.court.activity_type.image}/>
                        </div>
                        <div className="content">
                            <div className="main">
                                <h3 className="name">{this.props.item.court.name}</h3>
                                <p className="profession">{this.props.item.start_at}</p>
                                <p className="text-center">{this.props.item.court.description}</p>
                            </div>
                            <div className="footer">
                                <button className="btn btn-simple" onClick={this.rotateCard.bind(this)}>
                                    <i className="fa fa-mail-forward"></i> More...
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="back">
                        <div className="header">
                            <h5 className="motto">"To be or not to be, this is my awesome motto!"</h5>
                        </div>
                        <div className="content">
                            <div className="main">
                                <h4 className="text-center">Job Description</h4>
                                <p className="text-center">Web design, Adobe Photoshop, HTML5, CSS3, Corel and many others...</p>

                                <div className="stats-container">
                                    <div className="stats">
                                        <h4>235</h4>
                                        <p>
                                            Followers
                                        </p>
                                    </div>
                                    <div className="stats">
                                        <h4>114</h4>
                                        <p>
                                            Following
                                        </p>
                                    </div>
                                    <div className="stats">
                                        <h4>35</h4>
                                        <p>
                                            Projects
                                        </p>
                                    </div>
                                </div>

                            </div>
                        </div>
                        <div className="footer">
                            <button className="btn btn-simple" rel="tooltip" title="Flip Card" onClick={this.rotateCard.bind(this)}>
                                <i className="fa fa-reply"></i> Back
                            </button>
                            <div className="social-links text-center">
                                <a href="http://deepak646.blogspot.in/" className="facebook"><i className="fa fa-facebook fa-fw"></i></a>
                                <a href="http://deepak646.blogspot.in/" className="google"><i className="fa fa-google-plus fa-fw"></i></a>
                                <a href="http://deepak646.blogspot.in/" className="twitter"><i className="fa fa-twitter fa-fw"></i></a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )}
}

export default PublicEvent
