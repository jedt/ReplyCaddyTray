import React from 'react';
import './ModalChat.css'; // Create or update your CSS file

const ModalChat = ({ isOpen, onClose, children }) => {
  return (
    <div className={`modal-chat ${isOpen ? 'open' : ''}`}>
      <div className="modal-chat-content-tranparent">
        <div className="modal-chat-roundContainer">
          <div className="chat-header">
            <button className="apps-button" onClick={onClose}>
              <div style={{display: 'flex', alignItems: 'center'}}>
                <img src={"./images/apps-icon.png"} alt={"edit"} />
              </div>
            </button>
            <button className="close-button" onClick={onClose}>
              <div style={{display: 'flex', alignItems: 'center'}}>
                <img src={"./images/close-icon.png"} alt={"edit"} />
              </div>
            </button>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
};

export default ModalChat;
