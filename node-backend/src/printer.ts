import { Router, Request, Response } from 'express';
import fs from 'fs';
import path from 'path';
import ipp from 'ipp';

const router = Router();
const PRINTER_URL =
  process.env.PRINTER_URL ?? 'http://192.168.0.50:631/ipp/print';

router.get(
  '/print',
  (_req: Request, res: Response): void => {
    const file = path.join(__dirname, '../images/sample.jpg');
    if (!fs.existsSync(file)) {
      res.status(404).send('이미지 없음');
      return;
    }

    const data = fs.readFileSync(file);
    const printer = ipp.Printer(PRINTER_URL);

    printer.execute(
      'Print-Job',
      {
        'operation-attributes-tag': {
          'requesting-user-name': 'chakboot',
          'job-name': 'ChakBoot Print',
          'document-format': 'image/jpeg',
        },
        data,
      },
      (err: unknown) =>
        err
          ? res.status(500).send('출력 실패')
          : res.send('출력 완료'),
    );
  },
);

export default router;
