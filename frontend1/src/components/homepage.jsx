import React from 'react'
import "./homepage.css"
import Navbar from "./navbar"
// import { Link } from 'react-router-dom';

const homepage = () => {
  return (
    <div>
      <Navbar />
      <section style={styles.whiteSection} className="main">
        <div className="title">
          <p>DETECTIVE ZERO-DAY</p>
        </div>
        {/* <div className="img">
          <img alt='' src="https://img.freepik.com/free-photo/fading-blue-background_53876-88684.jpg?w=740&t=st=1686293300~exp=1686293900~hmac=532bc32306c49f2a05dcab37e96df94905086ebd8a2ea079c5120aacb030d084" style={styles.image} />
        </div> */}
        <div className="content">
          <p>Don't compromise your network's security. Get started with our powerful network log analysis tool today and experience the peace of mind that comes with knowing your systems are safe from cyber threats.</p>
          <a href="/signup">
            <button className="signup">Sign up</button>
          </a>

        </div>
        <br></br>
        <br></br>
        <div className="cards">
          <div className="xyz">
            <img alt='' src="https://www.seekpng.com/png/full/10-104124_line-transparent-shadow-white-vertical-line-transparent.png" style={styles.xyz} />
          </div>
          <div>
            <p className="biggertext">98%</p>
            <p className="smallertext">accuracy rate</p>
          </div>
          <div className="xyz">
            <img alt='' src="https://www.seekpng.com/png/full/10-104124_line-transparent-shadow-white-vertical-line-transparent.png" style={styles.xyz} />
          </div>
          <div>
            <p className="biggertext">ML</p>
            <p className="smallertext">LSTM and ISOLATION FOREST as the core model</p>
          </div>
          <div className="xyz">
            <img alt='' src="https://www.seekpng.com/png/full/10-104124_line-transparent-shadow-white-vertical-line-transparent.png" style={styles.xyz} />
          </div>
          <div>
            <p className="biggertext">20s</p>
            <p className="smallertext">avg. response time</p>
          </div>
          <div className="xyz">
            <img alt='' src="https://www.seekpng.com/png/full/10-104124_line-transparent-shadow-white-vertical-line-transparent.png" style={styles.xyz} />
          </div>
        </div>

      </section>
      <section className="section2">
        <div className="img2">
          <img alt='' src="https://img.freepik.com/free-photo/fading-blue-background_53876-88684.jpg?w=740&t=st=1686293300~exp=1686293900~hmac=532bc32306c49f2a05dcab37e96df94905086ebd8a2ea079c5120aacb030d084" style={styles.secimg}></img>
        </div>
        <div className="content2">
          <p style={{ fontWeight: "bold" }}>ZERO-DAY ATTACK</p>
          <p>Zero-day attacks exploit unknown vulnerabilities, making them highly elusive and dangerous.
            Our advanced system detects and predicts zero-day attacks, providing proactive defense.
            Stay one step ahead of cyber threats with our robust zero-day attack detection.</p>
          <a href="/about" className="aboutus">
            Read More
          </a>
          {/* <button  Link to="/about" className="aboutus">Read More</button> */}

        </div>
      </section >
      <section style={styles.Section3}>
        <div className="today">
          <p>Sign up today.</p>
        </div>
        <div className="startb">
          <a href="/signup">
            <button className="start">Get Started</button>
          </a>

        </div>
      </section>
      <footer className="footer">
        <div className="contact-details">
          <span>Copyrights Sri Vignesh S</span>
        </div>
      </footer>

    </div>
  )
}

export default homepage

const styles = {
  whiteSection: {
    backgroundColor: 'white',
    height: '400px',
  },
  image: {
    width: '60%',
    height: '50%',
    borderRadius: '0.5em',
  },
  xyz: {
    width: "30%"
  },
  secimg: {
    width: '90%',
    height: '50%',
    borderRadius: '0.5em',
  },
  Section3: {
    backgroundColor: 'white',
    height: '210px',
  },
};