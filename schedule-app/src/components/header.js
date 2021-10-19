import React from 'react';
import { Navbar, Nav, Container } from 'react-bootstrap'

class Header extends React.Component {

  constructor(props) {
    super(props);
    this.state = { active: null };
  }

  handleSelect(key) {
    this.setState({active: key});
  }

  render_() {
    return (
      <Container>
        <Nav 
          variant="tabs"
          activeKey={this.state.active}
          onSelect={this.handleClick.bind(this)}
        >
          <Navbar.Brand href="/">Scheduler</Navbar.Brand>
          <Nav.Item eventKey='/events'>
            <Nav.Link href="/events">Events</Nav.Link>
          </Nav.Item>
          <Nav.Item eventKey="/schedule">
            <Nav.Link href="/schedule">Schedule</Nav.Link>
          </Nav.Item>
        </Nav>
      </Container>
    );
  }

  render() {
    return (
      <Navbar variant='light' bg='light'>
        <Container>
          <Nav
            className="me-auto"
            variant='tabs'
            activeKey={this.state.active}
            onSelect={this.handleSelect.bind(this)}
          >
            <Navbar.Brand href="/">Scheduler</Navbar.Brand>
            <Nav.Link eventKey="events" href="#">Events</Nav.Link>
            <Nav.Link eventKey="schedule" href="#">Schedule</Nav.Link>
          </Nav>
          <Navbar.Text>:)</Navbar.Text>
        </Container>
      </Navbar>
    );
  }

}

export default Header;
