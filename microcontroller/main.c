//
// Included Files
//
#include "driverlib.h"
#include "device.h"
#include "board.h"
#include "scicomm.h"

volatile Protocol_Header_t g_prot_header = {CMD_NONE,0};
volatile int g_dado;
#define MAX_ELEMENTOS 512
uint16_t vect[MAX_ELEMENTOS]; // buffer global seguro
//
// Função Principal
//
void main(void)
{
    // Inicialização do dispositivo
    Device_init(); // define clock
    Interrupt_initModule();// inicializa int e a tabela de inte
    Interrupt_initVectorTable();//
    Board_init(); // so chama

    // Habilita interrupções globais e de tempo real
    EINT;
    ERTM;

    while (1)
    {
        if (g_prot_header.cmd != CMD_NONE)
        {
            switch (g_prot_header.cmd)
            {
                case CMD_RECEIVE_INT:
                   protocolReceiveInt(SCI0_BASE, vect, MAX_ELEMENTOS);
                    break;

                case CMD_SEND_INT:
                    protocolSendInt(SCI0_BASE, vect, MAX_ELEMENTOS);
                    break;
            }

            // Limpa status de interrupção e reseta comando
            SCI_clearInterruptStatus(SCI0_BASE, SCI_INT_RXFF);
            g_prot_header.cmd = CMD_NONE;
        }
    }
}

//
// Rotina de Interrupção da SCI (Recepção)
//
__interrupt void INT_SCI0_RX_ISR(void)
{
    uint16_t header[PROTOCOL_HEADER_SIZE];
    uint16_t cmd;

    SCI_readCharArray(SCI0_BASE, header, PROTOCOL_HEADER_SIZE);
    cmd = header[0];
    g_prot_header.data_len = header[1] | (header[2] << 8);
    g_prot_header.cmd = (cmd < CMD_COUNT)? (SCI_Command_e)cmd : CMD_NONE;

    Interrupt_clearACKGroup(INT_SCI0_RX_INTERRUPT_ACK_GROUP);
}
