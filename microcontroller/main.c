//
// Included Files
//
#include "driverlib.h"
#include "device.h"
#include "board.h"
#include "scicomm.h"

volatile Protocol_Header_t g_prot_header = {CMD_NONE,0};
volatile int g_dado;
#define MAX_ELEMENTOS 1000
uint16_t vect[MAX_ELEMENTOS]; // buffer global seguro
#pragma DATA_SECTION(vect, ".memoria1");
#define TAM_BUFFER_DAC 1000
#define TAM_BUFFER_ADC 500
//extern uint16_t dac_buffer[];
volatile uint16_t adc_buffer[TAM_BUFFER_ADC] = {0};
#pragma DATA_SECTION(adc_buffer, ".memoria1");
volatile uint16_t g_senoide[TAM_BUFFER_DAC] = {0};
#pragma DATA_SECTION(g_senoide, ".memoria1");
volatile float gain = 1.0f;
volatile bool flag = false;


// Função Principal
//
void main(void)
{
    // Inicialização do dispositivo
    Device_init(); // define clock
    Interrupt_initModule();// inicializa int e a tabela de int
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
                   flag = 1;
                    break;

                case CMD_SEND_INT:
                    //protocolSendInt(SCI0_BASE, adc_buffer, MAX_ELEMENTOS);
                    protocolSendInt(SCI0_BASE, adc_buffer, TAM_BUFFER_ADC);

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


__interrupt void INT_ADC0_1_ISR(void)
{
    static uint16_t cnt_adc = 0;
    cnt_adc = (cnt_adc+1)%TAM_BUFFER_ADC;
    adc_buffer[cnt_adc] = ADC_readResult(ADC0_RESULT_BASE, ADC0_SOC0);
    ADC_clearInterruptStatus(ADC0_BASE, ADC_INT_NUMBER1);
    Interrupt_clearACKGroup(INT_ADC0_1_INTERRUPT_ACK_GROUP);

}

__interrupt void INT_myCPUTIMER1_ISR(void)
{
    static uint16_t cnt_dac = 0;
//    if(gain * vect[cnt_dac] > 4095)
//    {
//        vect[cnt_dac] = 4095
//    }
    DAC_setShadowValue(DAC0_BASE, ((gain * vect[cnt_dac]))); // O DAC é de 16 bits e os valores são de 16 bits por isso a divisão
    //DAC_setShadowValue(DAC0_BASE, SCI_writeCharArray(sci_base, txBuf, INT_SIZE));
    g_senoide[cnt_dac] = gain * vect[cnt_dac];
    cnt_dac = (cnt_dac+1)%TAM_BUFFER_DAC;
}
