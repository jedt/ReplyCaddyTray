import React, {useEffect, useState, useReducer, useRef} from 'react';
import { Dot } from 'react-animated-dots';
import { motion } from 'framer-motion';
import './Dashboard.css';
import './DocumentList'
import {micromark} from "micromark";
import PanelChat from "./PanelChat";
import {Image} from "./helpers/ImageHelper";
import useWebSocket, { ReadyState }  from 'react-use-websocket';
import {Outlet, useNavigate} from 'react-router-dom';
const WS_URL = 'ws://127.0.0.1:8765';

// declare and use Roboto Flex font
const transitionPanel = { type: 'linear', duration: 0.06 };

// extend css
const styles = {
  title: {
    fontFamily: 'Roboto Flex',
    color: 'white',
    fontSize: '19px',
    paddingBottom: '10px',
    paddingTop: '10px',
  },
  sidebarIcon: {
    color: 'black',
  },
};

function buttonClick() {
  console.log('Button clicked');
}

function buttonElementHomeActive() {
  return (
    <button className={"sidebar-btn active"} onClick={buttonClick}>
      <div className={"sidebar-btn-container"}>
        <div className={"buttonImage"}>
          <Image width={28} height={28} style={styles.sidebarIcon} src={"./images/home.png"} alt={"home"} />
        </div>
        <div className={"buttonText"}>
          <span>Home</span>
        </div>
      </div>
    </button>
  );
}


function Dashboard() {
  const navigate = useNavigate()
  const [, forceUpdate] = useReducer(x => x + 1, 0);
  const [shouldShowChatPanel, setShouldShowChatPanel] = useState(false);
  const [messageHistoryMap, setMessageHistoryMap] = useState({});
  const [lastMessageID, setLastMessageID] = useState(null);
  const [chunks, setChunks] = useState([]);
  const [promptText, setPromptText] = useState('Explain why exoplanets are important');
  const messagesEndRef = useRef(null)
  const scrollToBottom = () => {
    messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
  }
  let ws;

  function buttonElement(buttonText, iconFilePath) {
    return (
      <button className={"tray-btn"} onClick={()=>{
        // route the page using react router to /settings
        navigate('/settings');
      }}>
        <div style={{display: 'flex', alignItems: 'center'}}>
          <img style={styles.sidebarIcon} src={iconFilePath} alt={buttonText} />
          {buttonText}
        </div>
      </button>
    );
  }

  const { sendMessage, lastMessage, readyState } = useWebSocket(WS_URL, {
    onOpen: () => {
      console.log('WebSocket connection established.');
    },
    onMessage: (event) => {
      try {
        let responseJson = JSON.parse(event.data);
        if (responseJson.hasOwnProperty('id')) {
          //if id == start_of_response
          if (responseJson.id === 'start_of_response') {
            // create a new messageHistory entry for the chunks using the lastMessageID
            setMessageHistoryMap((prev) => {
              return {
                ...prev,
                [lastMessageID]: '',
              };
            });
            setTimeout(()=>{
              scrollToBottom()
            })
          }
          //if id == end_of_response
          else if (responseJson.id === 'end_of_response') {
            // set the messageHistory entry for the lastMessageID
            setMessageHistoryMap((prev) => {
              return {
                ...prev,
                [lastMessageID]: micromark(chunks.join('')),
              };
            });
            forceUpdate();
            setChunks([]);
            setTimeout(()=>{
              scrollToBottom()
            })

          }
          else {

            // add the chunk to the chunks array
            // example response: {"id": "chunk_response", "content": " best"}
            if (responseJson.hasOwnProperty('content')) {

              //async setChunks setMessageHistoryMap
              setChunks((prev) => {
                return [...prev, responseJson.content];
              });
              setMessageHistoryMap((prev) => {
                return {
                  ...prev,
                  [lastMessageID]: micromark(chunks.join('') + responseJson.content),
                };
              });
              forceUpdate();
            }
          }
        }
      }
      catch (e) {
        console.error('Error parsing JSON:', e);
      }

    },
    shouldReconnect: (closeEvent) => true,
  });


  function renderMessageHistoryMap() {
    /*
      <div className={"chat-message"}>
        <div className={"assistant-message"}>
          <span>Hi, how can I help you? Need some help with your documents? Just ask me</span>
        </div>
      </div>
   */
    return Object.keys(messageHistoryMap).map((key) => {
      // if content is empty, render dots
      if (messageHistoryMap[key] === '') {
        return (
          <div className={"dots"}>
            <div className={"chat-message"}>
              <div className={"assistant-message"}>
                <Dot>.</Dot>
                <Dot>.</Dot>
                <Dot>.</Dot>
              </div>
            </div>
          </div>
        );
      }
      else {
        return (
          <div className={"chat-message"}>
            <div className={"assistant-message"}>
              <div dangerouslySetInnerHTML={{__html: messageHistoryMap[key]}}/>
            </div>
          </div>
        );
      }
    });
  }

  return (
    <div className="App">
      <motion.div
        className="main-left"
        initial="expanded"
        animate={shouldShowChatPanel ? 'expanded' : 'shrank'}
        variants={{
          expanded: { width: '80%' },
          shrank: { width: '100%' },
        }}
        transition={transitionPanel}
      >
        <header className="App-header">
          <div className={"header-logo"}>
            <h1 style={styles.title}>Hello, world</h1>
          </div>
          <div className={"header-tray"}>
            <button className={"header-tray-btn"} onClick={()=>{
              navigate('/settings');
            }}>
              <div className={"header-tray-item"}>
                <div style={{display: 'flex', alignItems: 'center'}}>
                  <Image width={21} height={20} src={"./images/settings.png"} alt={"settings"} />
                </div>
              </div>
            </button>
            <button className={"header-tray-btn"} onClick={()=>{
              setShouldShowChatPanel(true);
            }}>
              <div className={"header-tray-item"}>
                <div style={{display: 'flex', alignItems: 'center'}}>
                  <Image width={21} height={20} src={"./images/edit-document.png"} alt={"edit"} />
                </div>
              </div>
            </button>
          </div>
        </header>
        <div className={"main-wrapper"}>
          <div className={"sidebar"}>
              <ul className={"sidebar-nav"}>
                <li>
                  {buttonElementHomeActive()}
                </li>
                <li>
                  <button className={"sidebar-btn"} onClick={()=>{
                    // route the page using react router to /settings
                    // navigate('/settings');
                  }}>
                    <div className={"sidebar-btn-container"}>
                      <div className={"buttonImage"}>
                        <Image height={33} style={styles.sidebarIcon} src={'./images/document.png'} alt={'Documents'} />
                      </div>
                      <div className={"buttonText"}>
                        <span>Text Documents</span>
                      </div>
                    </div>
                  </button>
                  {/*{buttonElement("Documents", "./images/document.png")}*/}
                </li>
                <li>
                  <button className={"sidebar-btn"} onClick={()=>{
                    // route the page using react router to /settings
                    // navigate('/settings');
                  }}>
                    <div style={{display: 'flex', alignItems: 'center'}}>
                      <Image height={33} style={styles.sidebarIcon} src={'./images/side-pdf-icon.png'} alt={'Documents'} />
                      PDFs
                    </div>
                  </button>
                </li>
              </ul>
          </div>
          <Outlet />
        </div>
      </motion.div>
      <motion.div
        className={"right-panel"}
        initial="closed"
        animate={shouldShowChatPanel ? 'open' : 'closed'}
        variants={{
          open: { x: 0, opacity: 1, width: '50%', flex: 1 },
          closed: { x: '100%', opacity: 0, width: '0%', flex: 0 },
        }}
        transition={transitionPanel}
        exit={{ x: '100%', opacity: 0 }}
      >
        <PanelChat
            isOpen={shouldShowChatPanel}
            onPressApp={()=>{
              let longText = `Exoplanets, which are planets that orbit stars other than the Sun, have revolutionized our understanding of planetary formation and the search for life beyond Earth. Here's why they're so important:
  Understanding Planetary Formation: The discovery of exoplanets has provided a unique opportunity to study how planets form and evolve in different environments. By analyzing the properties of exoplanets, such as their size, mass, and orbital characteristics, scientists can gain insights into the processes that shape planetary systems.
  Search for Life Beyond Earth: Exoplanets offer a potential haven for life beyond our solar system. With thousands of potentially habitable exoplanets discovered so far, the possibility of finding life on one or more of them is becoming increasingly plausible. This has sparked intense research and excitement in the scientific community.
  Implications for Astrobiology: The study of exoplanets helps us understand the conditions necessary for life to arise and thrive. By examining the atmospheric properties, temperature ranges, and surface environments of exoplanets, scientists can refine our understanding of what makes a planet habitable and identify potential biosignatures (signs of biological activity).`
              let lastMessageID = new Date().getTime();
              setChunks([]);
              setLastMessageID(lastMessageID);
              setMessageHistoryMap((prev) => {
                return {
                  ...prev,
                  [lastMessageID]: longText,
                };
              });
              setTimeout(()=>{
                scrollToBottom();
              }, 1)

            }}
            onClose={()=>{
              setShouldShowChatPanel(false);
            }}
        >
          <div className={"chat-body"}>
              <div className={"chat-interactions"}>
                <div className={"scrollable-list-chat"}>
                  {renderMessageHistoryMap()}
                  {/*<div className={"chat-message"}>*/}
                  {/*  <div className={"user-message"}>*/}
                  {/*    <span>Provide a simple pie chart</span>*/}
                  {/*  </div>*/}
                  {/*</div>*/}
                  <div style={{"height": "20px"}} ref={messagesEndRef} />
                </div>
              </div>
              <div className={"chat-footer"}>
                <div className={"input-user-chat-wrapper"}>
                  <div className={"input-text-wrapper"}>
                    <input type={"text"} placeholder={"Type your message"}
                        value={promptText}
                        onChange={(e) => {
                          setPromptText(e.target.value);
                        }}
                    />

                    <div className={"send-button-wrapper"}>
                      <button className={"send-button"} onClick={(e)=>{
                        let messageHistoryID = new Date().getTime();
                        setChunks([]);
                        setLastMessageID(messageHistoryID);
                        setMessageHistoryMap((prev) => {
                          return {
                            ...prev,
                            [messageHistoryID]: '',
                          };
                        });

                        sendMessage(JSON.stringify({promptText, messageHistoryID}));
                        e.preventDefault()
                      }}>
                        <Image width={28} height={28} src={"./images/send-button.png"} alt={"send"} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
        </PanelChat>
      </motion.div>
    </div>
  );
}

export default Dashboard;
