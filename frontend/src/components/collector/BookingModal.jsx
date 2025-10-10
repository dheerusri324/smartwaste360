// frontend/src/components/collector/BookingModal.jsx
import React, { useState } from 'react';
import { Modal } from '../common';

const BookingModal = ({ colony, isOpen, onClose, onSubmit }) => {
  const today = new Date().toISOString().split('T')[0];
  const [bookingDate, setBookingDate] = useState(today);
  const [timeSlot, setTimeSlot] = useState('Morning (9am - 12pm)');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    try {
      await onSubmit({
        colony_id: colony.colony_id,
        booking_date: bookingDate,
        time_slot: timeSlot,
      });
      onClose();
    } catch (err) {
      setError('Failed to schedule booking. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !colony) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Schedule Pickup for ${colony.colony_name}`}>
      <div className="space-y-4">
        {error && <p className="text-red-500 text-sm">{error}</p>}
        <div>
          <label htmlFor="bookingDate" className="form-label">Select Date</label>
          <input
            id="bookingDate"
            type="date"
            value={bookingDate}
            onChange={(e) => setBookingDate(e.target.value)}
            min={today}
            className="form-input"
          />
        </div>
        <div>
          <label htmlFor="timeSlot" className="form-label">Select Time Slot</label>
          <select id="timeSlot" value={timeSlot} onChange={(e) => setTimeSlot(e.target.value)} className="form-input">
            <option>Morning (9am - 12pm)</option>
            <option>Afternoon (1pm - 4pm)</option>
            <option>Evening (5pm - 8pm)</option>
          </select>
        </div>
        <div className="flex justify-end gap-4 pt-4">
          <button onClick={onClose} className="btn-secondary">Cancel</button>
          <button onClick={handleSubmit} disabled={loading} className="btn-primary">
            {loading ? 'Scheduling...' : 'Confirm Booking'}
          </button>
        </div>
      </div>
    </Modal>
  );
};
export default BookingModal;