import express from 'express';
import cors from 'cors';
import printerRoutes from './printer';
import cameraRoutes from './camera';

const app = express();
app.use(cors());
app.use('/api', printerRoutes);
app.use('/api', cameraRoutes);

const PORT = process.env.PORT ?? 8085;
app.listen(PORT, () => console.log(`✅ Node backend up on :${PORT}`));
