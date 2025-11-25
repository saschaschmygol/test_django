// src/pages/Tickets.tsx
import { useCallback, useEffect, useState } from 'react';
import { TicketService } from '../services/tickets';
import { useNavigate } from 'react-router-dom';
import { Box, Card, CardContent, Typography, Button } from '@mui/material';
import Grid from '@mui/material/Grid';

export interface Ticket {
  id: number;
  status: string;
  user_id: number | null;
  chat_id: number;
  timestamp: string;
}

export default function Tickets() {
  const [my, setMy] = useState<Ticket[]>([]);
  const [open, setOpen] = useState<Ticket[]>([]);
  const navigate = useNavigate();

  const load = useCallback(async () => {
    setMy(await TicketService.getMyTickets());
    setOpen(await TicketService.getOpenTickets());
  }, []);

  useEffect(() => {
    Promise.resolve().then(() => load());
  }, [load]);

  async function take(ticket_id: number) {
    await TicketService.assign(ticket_id);
    load();
  }

  return (
    <Box sx={{ p: 4 }}>
      <Grid container spacing={4}>
        {/* Назначенные мне */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Typography variant="h6" mb={2} color="success.main">
            Назначенные мне
          </Typography>
          {my.map((t) => (
            <Card key={`my-${t.id}`} sx={{ mb: 2, backgroundColor: '#004d00' }}>
              <CardContent sx={{ color: '#fff' }}>
                <Typography>
                  #{t.id} — {t.status}
                </Typography>
                <Button
                  variant="outlined"
                  sx={{ mt: 1, color: '#fff', borderColor: '#fff' }}
                  onClick={() => navigate(`/ticket/${t.id}`)}>
                  Открыть
                </Button>
              </CardContent>
            </Card>
          ))}
        </Grid>

        {/* Не назначенные */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Typography variant="h6" mb={2} color="error.main">
            Не назначенные
          </Typography>
          {open.map((t) => (
            <Card key={`open-${t.id}`} sx={{ mb: 2, backgroundColor: '#4d0000' }}>
              <CardContent sx={{ color: '#fff' }}>
                <Typography>
                  #{t.id} — {t.status}
                </Typography>
                <Button
                  variant="outlined"
                  sx={{ mt: 1, color: '#fff', borderColor: '#fff' }}
                  onClick={() => take(t.id)}>
                  Взять тикет
                </Button>
              </CardContent>
            </Card>
          ))}
        </Grid>
      </Grid>
    </Box>
  );
}
