import { Router } from 'express';
import NodeWebcam from 'node-webcam';
import path from 'path';

const router = Router();
const cam = NodeWebcam.create({ width: 640, height: 480, saveShots: true });

router.get('/capture', (_req, res) => {
  const fileName = `snapshot_${Date.now()}.jpg`;
  NodeWebcam.capture(path.join(process.cwd(), fileName), {}, err =>
    err ? res.status(500).send('촬영 실패') : res.sendFile(path.join(process.cwd(), fileName)),
  );
});

export default router;
