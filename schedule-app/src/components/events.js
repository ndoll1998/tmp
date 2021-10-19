import React from 'react'
import { Container, Accordion, Card, Button, Row, Col, Tabs, Tab } from 'react-bootstrap'
import './events.css'

class Event extends React.Component {
  
  render() {
    return (
      <Accordion flush>
        <Accordion.Item eventKey="0">
          
          <Accordion.Header> 
            <Row>
              <Col md="auto">
                {this.props.name} <br/> 
                {this.props.lecturers.map(l => {return l.lecturer}).join(", ")}
              </Col>
              <Col md="auto">
                <Button 
                  variant='outline-success' 
                  onClick={() => this.props.handleSelect(this.props.eventId)}
                >Select</Button>
              </Col>
            </Row>
          </Accordion.Header>
          
          <Accordion.Body> Lorim Ipsum </Accordion.Body>
        </Accordion.Item>
      </Accordion>
    );
  }

}

class SelectedEvent extends React.Component {
  
  render() {
    return (
      <Accordion flush>
        <Accordion.Item eventKey="0">
          
          <Accordion.Header> 
            {this.props.name} <br/> 
            {this.props.lecturers.map(l => {return l.lecturer}).join(", ")}
            <Button 
              variant='outline-danger' 
              onClick={() => this.props.handleSelect(this.props.eventId)}
            >Remove</Button>
          </Accordion.Header>
          
          <Accordion.Body> Lorim Ipsum </Accordion.Body>
        </Accordion.Item>
      </Accordion>
    );
  }

}


class Events extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      events: [
        {
          eventId: "1",
          name: "Pattern Recognition I",
          type: "Lecture",
          workload: "6.0",
          lecturers: [
            { lecturer: "Christian Bauckhage", role: "1" }, 
            { lecturer: "Stefan Wrobel", role: null }
          ],
          times: [
            { weekday: "Mo", from: "10:15", to: "11:45" },
            { weekday: "Tu", from: "10:15", to: "11:45" }
          ]
        },
        {
          eventId: "2",
          name: "Pattern Recognition II",
          type: "Lecture",
          workload: "6.0",
          lecturers: [
            { lecturer: "Christian Bauckhage", role: "1" }, 
            { lecturer: "Stefan Wrobel", role: null }
          ],
          times: [
            { weekday: "Mo", from: "10:15", to: "11:45" },
            { weekday: "Tu", from: "10:15", to: "11:45" }
          ]
        }
      ],
      selected_events: []
    }

    // bind event handlers
    this.handleSelectEvent = this.handleSelectEvent.bind(this);
    this.handleUnselectEvent = this.handleUnselectEvent.bind(this);
  }

  handleSelectEvent(eventId) {
    this.setState(state => {
        let e = state.events.filter(e => 
          { return e.eventId === eventId; 
        });
        return { 
          events: state.events.filter(e => { 
            return e.eventId !== eventId; 
          }),
          selected_events: [...state.selected_events, ...e] 
        }
      }
    );
  }

  handleUnselectEvent(eventId) {
    this.setState(state => {
        let e = state.selected_events.filter(e => { 
          return e.eventId === eventId; 
        });
        return { 
          selected_events: state.selected_events.filter(e => { 
            return e.eventId !== eventId;
          }),
          events: [...state.events, ...e] 
        }
      }
    );
  }

  render() {
    return (
      <Container>
        <Row>

          <Col style={{minWidth: "300px"}}>
            <Card style={{margin: "10px 0px"}}>
              <Card.Header> Selected Events </Card.Header>
              <Card.Body style={{padding: "0px"}}>
                {(this.state.selected_events.length > 0)?
                  this.state.selected_events.map(e => {
                    return (
                      <>
                        <SelectedEvent 
                          {...e}
                          handleSelect={this.handleUnselectEvent} 
                        />
                        <div className="separator" />
                    </>
                  );
                }) : <p> Whoops, looks like you have no events selected yet! </p>}
              </Card.Body>
            </Card>
          </Col>

          <Col style={{minWidth: "300px"}}>
            <Card style={{margin: "10px 0px"}}>
              <Card.Header> All Events </Card.Header>
            <Card.Body style={{padding: "0px"}}>
              {this.state.events.map(e => {
                return (
                  <>
                    <Event 
                      {...e} 
                      handleSelect={this.handleSelectEvent} 
                    />
                    <div className="separator" />
                  </>
                );
              })}
            </Card.Body>
          </Card>
          </Col>

        </Row>
      </Container>
    );
  }

}

export default Events;
