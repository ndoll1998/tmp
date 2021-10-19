import React from 'react'
import Header from './components/header'
import Events from './components/events'
import Schedule from './components/schedule'
import Landing from './components/landing'
import { BrowserRouter as Router, Switch, Route, NavLink } from 'react-router-dom';
import { withRouter } from 'react-router'
import './App.css'

import { Container, Navbar, Nav } from 'react-bootstrap'

class Navigation extends React.Component {

  render() {
    return (
      <>
        <Navbar sticky='top' bg='light' variant='light'>
          <Container>
            <Navbar.Brand href="/">Scheduler</Navbar.Brand>
            <Nav 
              variant='tabs'
              className="justify-content-center"
              activeKey={this.props.location.pathname}
            >
              <Nav.Link href='/events'>Events</Nav.Link>
              <Nav.Link href='/schedule'>Schedule</Nav.Link>
            </Nav>
            <Nav className="justify-content-end">
              <Nav.Link href="/about">About</Nav.Link>
            </Nav>
          </Container>
        </Navbar>
        <div className="border" />
      </>
    );
  }

}

const NavWithRouter = withRouter(Navigation);

class App extends React.Component {

  render() {
    return (
      <div className="App">
        <Router>
          <NavWithRouter /> 
          <Switch>
            <Route path="/events"><Events /></Route>
            <Route path="/schedule"><Schedule /></Route>
            <Route path="/"><Landing /></Route>
          </Switch>
        </Router>
      </div>
    );
  }

}

export default App;
