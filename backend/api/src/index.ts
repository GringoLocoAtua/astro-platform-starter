import express from 'express';
import { getBookingQuote } from './routes/bookingRoutes';

const app = express();
app.use(express.json());

app.get('/health', (_, res) => res.json({ status: 'ok', service: 'bu1st-api' }));
app.post('/v1/bookings/quote', getBookingQuote);

const port = process.env.PORT || 4000;
app.listen(port, () => {
  console.log(`BU1ST API running on ${port}`);
});
