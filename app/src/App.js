import React, {useEffect, useState} from 'react';
import './App.css';
import './DocumentList'
import DocumentList from "./DocumentList";
import MainHeader from "./MainHeader";
import ModalChat from "./ModalChat";

// declare and use Roboto Flex font
const font = new FontFace('Roboto Flex', 'url(./fonts/RobotoFlex-Regular.ttf)');

font.load().then(function(loaded_face) {
  // when document is ready
  document.addEventListener("DOMContentLoaded", () => {
    document.fonts.add(loaded_face);
    document.body.style.fontFamily = '"Roboto Flex", sans-serif';
  })
}).catch(function(error) {
  console.error('Failed to load font:', error);
});

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
      <div style={{display: 'flex', alignItems: 'center'}}>
        <img style={styles.sidebarIcon} src={"./images/home.png"} alt={"home"} />
        Home
      </div>
    </button>
  );
}
function buttonElement(buttonText, iconFilePath) {
  return (
    <button className={"tray-btn"} onClick={buttonClick}>
      <div style={{display: 'flex', alignItems: 'center'}}>
        <img style={styles.sidebarIcon} src={iconFilePath} alt={buttonText} />
        {buttonText}
      </div>
    </button>
  );
}



function App() {
  const [documents, setDocuments] = useState([]);
  const [shouldShowChatModal, setShouldShowChatModal] = useState(true);

  useEffect(() => {
    fetch('http://127.0.0.1:8971/api/data')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => setDocuments(data))
      .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <div className={"header-logo"}>
          <h1 style={styles.title}>Hello, world</h1>
        </div>
        <div className={"header-tray"}>
          <button className={"header-tray-btn"} onClick={()=>{
            setShouldShowChatModal(true);
          }}>
            <div className={"header-tray-item"}>
              <div style={{display: 'flex', alignItems: 'center'}}>
                <img src={"./images/edit-document.png"} alt={"edit"} />
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
              <li>{buttonElement("Documents", "./images/document.png")}</li>
              <li>{buttonElement("Settings", "./images/side-pdf-icon.png")}</li>
            </ul>
        </div>
        <div className={"mainSection"}>
          {MainHeader()}
          {DocumentList(documents)}
        </div>
        <ModalChat isOpen={shouldShowChatModal} onClose={()=>{
          setShouldShowChatModal(false);
        }}>
          <div className={"chat-body"}>
            <div className={"chat-interactions"}>
              <div className={"chat-message"}>
                <div className={"assistant-message"}>
                  <span>Hi, how can I help you? Need some help with your documents? Just ask me</span>
                </div>
              </div>
              <div className={"chat-message"}>
                <div className={"user-message"}>
                  <span>Provide a simple pie chart</span>
                </div>
              </div>
            </div>
            <div className={"chat-footer"}>
              <div className={"input-user-chat-wrapper"}>
                <div className={"input-text-wrapper"}>
                  <input type={"text"} placeholder={"Type your message"} />

                  <div className={"send-button-wrapper"}>
                    <button className={"send-button"}>
                      <img src={"./images/send-button.png"} alt={"send"} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </ModalChat>
      </div>
    </div>
  );
}

export default App;
