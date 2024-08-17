import React, {useEffect} from 'react';
import {Image} from './helpers/ImageHelper'
import './PanelChat.css'; // Create or update your CSS file

const PanelChat = ({ isOpen, onClose, onPressApp, children }) => {
  return (
    <div className={`panel-chat ${isOpen ? 'open' : ''}`}>
      <div className="panel-chat-roundContainer">
        <div className="chat-header">
          <button className="apps-button" onClick={onPressApp}>
            <div style={{display: 'flex', alignItems: 'center'}}>
              <Image width={16} height={16} src={"./images/apps-icon.png"} alt={"edit"} />
            </div>
          </button>
          <button className="close-button" onClick={onClose}>
            <div style={{display: 'flex', alignItems: 'center'}}>
              <Image width={16} height={16} src={"./images/close-icon.png"} alt={"edit"} />
            </div>
          </button>
        </div>
        {children}
      </div>
    </div>
  );
};

export default PanelChat;
