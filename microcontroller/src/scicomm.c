/*
 * scicomm.c
 *
 *  Created on: 13 de jun de 2025
 *      Author: Guilherme Márcio Soares
 */
#include "board.h"
#include "device.h"
#include "scicomm.h"

void protocolReceiveInt(unsigned int sci_base, uint16_t *vect, unsigned int MAX_ELEMENTOS)
{
    uint16_t buffer[INT_SIZE];
    for(int i = 0; i < MAX_ELEMENTOS; i++)
    {
        SCI_readCharArray(sci_base, buffer, INT_SIZE);
        vect[i] = (buffer[0] | (buffer[1] << 8U)); //Isso junta os dois bytes em um único int16_t (little endian)
    //*vect passando como ponteiro eu não preciso passar como parametro
    }
}
//
//void protocolSendInt(unsigned int sci_base, uint16_t *vect, unsigned int MAX_ELEMENTOS)
//{
//    uint16_t txBuf[INT_SIZE];
//    for(int i = 0; i < MAX_ELEMENTOS; i++)
//    {
//    txBuf[0] = (uint16_t)(vect[i] & 0x00FF);//Isso pega os 8 bits menos significativos do número.
//    txBuf[1] = (uint16_t)((vect[i] >> 8U) & 0x00FF);//Aqui ele desloca 8 bits para a direita (ou seja, pega a parte alta)
//    SCI_writeCharArray(sci_base, txBuf, INT_SIZE);
//
//    }
//    //SCI_writeCharArray(sci_base, txBuf, INT_SIZE);
//}

//void protocolSendInt(unsigned int sci_base, uint16_t *g_senoide, unsigned int TAM_BUFFER_ADC)
void protocolSendInt(unsigned int sci_base, volatile uint16_t *adc_buffer, unsigned int TAM_BUFFER_ADC)

{
    uint16_t txBuf[INT_SIZE];
    for(int i = 0; i < TAM_BUFFER_ADC; i++)
    {
    txBuf[0] = (uint16_t)(adc_buffer[i] & 0x00FF);//Isso pega os 8 bits menos significativos do número.
    txBuf[1] = (uint16_t)((adc_buffer[i] >> 8U) & 0x00FF);//Aqui ele desloca 8 bits para a direita (ou seja, pega a parte alta)
    SCI_writeCharArray(sci_base, txBuf, INT_SIZE);
    }
    //SCI_writeCharArray(sci_base, txBuf, INT_SIZE);
}
