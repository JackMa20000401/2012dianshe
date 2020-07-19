#include "sys.h"
#include "delay.h"
#include "usart.h" 
#include "led.h" 		 	 
#include "lcd.h" 
#include "key.h" 
#include "touch.h"  
#include "timer.h"  

////////////////////////////////////////////////////////////////////////////////
//电容触摸屏专有部分
//画水平线
//x0,y0:坐标
//len:线长度
//color:颜色
void gui_draw_hline(u16 x0,u16 y0,u16 len,u16 color)
{
	if(len==0)return;
	LCD_Fill(x0,y0,x0+len-1,y0,color);	
}
//画实心圆
//x0,y0:坐标
//r:半径
//color:颜色
void gui_fill_circle(u16 x0,u16 y0,u16 r,u16 color)
{											  
	u32 i;
	u32 imax = ((u32)r*707)/1000+1;
	u32 sqmax = (u32)r*(u32)r+(u32)r/2;
	u32 x=r;
	gui_draw_hline(x0-r,y0,2*r,color);
	for (i=1;i<=imax;i++) 
	{
		if ((i*i+x*x)>sqmax)// draw lines from outside  
		{
 			if (x>imax) 
			{
				gui_draw_hline (x0-i+1,y0+x,2*(i-1),color);
				gui_draw_hline (x0-i+1,y0-x,2*(i-1),color);
			}
			x--;
		}
		// draw lines from inside (center)  
		gui_draw_hline(x0-x,y0+i,2*x,color);
		gui_draw_hline(x0-x,y0-i,2*x,color);
	}
}  
//两个数之差的绝对值 
//x1,x2：需取差值的两个数
//返回值：|x1-x2|
u16 my_abs(u16 x1,u16 x2)
{			 
	if(x1>x2)return x1-x2;
	else return x2-x1;
}  
//画一条粗线
//(x1,y1),(x2,y2):线条的起始坐标
//size：线条的粗细程度
//color：线条的颜色
void lcd_draw_bline(u16 x1, u16 y1, u16 x2, u16 y2,u8 size,u16 color)
{
	u16 t; 
	int xerr=0,yerr=0,delta_x,delta_y,distance; 
	int incx,incy,uRow,uCol; 
	if(x1<size|| x2<size||y1<size|| y2<size)return; 
	delta_x=x2-x1; //计算坐标增量 
	delta_y=y2-y1; 
	uRow=x1; 
	uCol=y1; 
	if(delta_x>0)incx=1; //设置单步方向 
	else if(delta_x==0)incx=0;//垂直线 
	else {incx=-1;delta_x=-delta_x;} 
	if(delta_y>0)incy=1; 
	else if(delta_y==0)incy=0;//水平线 
	else{incy=-1;delta_y=-delta_y;} 
	if( delta_x>delta_y)distance=delta_x; //选取基本增量坐标轴 
	else distance=delta_y; 
	for(t=0;t<=distance+1;t++ )//画线输出 
	{  
		gui_fill_circle(uRow,uCol,size,color);//画点 
		xerr+=delta_x ; 
		yerr+=delta_y ; 
		if(xerr>distance) 
		{ 
			xerr-=distance; 
			uRow+=incx; 
		} 
		if(yerr>distance) 
		{ 
			yerr-=distance; 
			uCol+=incy; 
		} 
	}  
}   

int main(void)
{	
	u8 info_type = 0;
	u16 t, len, lastdx=0, lastdy=0;
	u8 direction = 0, ring = 0;
	u8 new_direction, new_ring;
	int radius, dx = 0, dy = 0;
	float px=0.02,py=0.01,ix=0.001,iy=0.0005;
	char xy[20];	
	
 	Stm32_Clock_Init(9);	//系统时钟设置
	uart_init(72,115200);	//串口初始化为115200
	delay_init(72);	   	 	//延时初始化 
	LED_Init();		  		//初始化与LED连接的硬件接口
	LCD_Init();			   	//初始化LCD
	KEY_Init();				//按键初始化		 	
	tp_dev.init();			//触摸屏初始化 
    TIM3_PWM_Init(14399,100);	//不分频。PWM频率=72000000/(14399+1)/100=50hz
	TIM1_PWM_Init(14399,100);


	gui_fill_circle(240,400,230,BLACK);
	
	gui_fill_circle(240,400,220,WHITE);
	gui_fill_circle(240,400,190,BLACK);
	
	gui_fill_circle(240,400,180,WHITE);
	gui_fill_circle(240,400,150,BLACK);
	
	gui_fill_circle(240,400,140,WHITE);
	gui_fill_circle(240,400,110,BLACK);
	
	gui_fill_circle(240,400,100,WHITE);
	gui_fill_circle(240,400,70,BLACK);
	
	gui_fill_circle(240,400,60,WHITE);
    gui_fill_circle(240,400,30,RED);
	
	delay_ms(1000)	;
	
	PB5=13490;
	
	PA8=450;
	
	LCD_ShowString(10, 30, 200, 24, 16, "radius:");
	LCD_ShowString(10, 50, 200, 24, 16, "dx:");
	LCD_ShowString(10, 70, 200, 24, 16, "dy:");
	LCD_ShowString(10, 90, 200, 24, 16, "dir:");
	LCD_ShowString(10, 110, 200, 24, 16, "ring:");
	
  while(1)
	{

     while(!PA1)
     {
		if(USART_RX_STA&0x8000)
		{					   
			len=USART_RX_STA&0x3FFF;//得到此次接收到的数据长度
			
			if( 0 == info_type ) {
				if( USART_RX_BUF[0] == 'r' && USART_RX_BUF[1] == ':' ) {
					radius = (USART_RX_BUF[2]-'0')*100 + (USART_RX_BUF[3]-'0')*10 + (USART_RX_BUF[4]-'0');
					LCD_ShowxNum(60, 30, radius, 3, 16, 0);
					info_type = 1;
				}
			}
			else {
				dx = (USART_RX_BUF[1]-'0')*100 + (USART_RX_BUF[2]-'0')*10 + (USART_RX_BUF[3]-'0');
				if( USART_RX_BUF[0] == '-' )
					dx = -dx;
				dy = (USART_RX_BUF[5]-'0')*100 + (USART_RX_BUF[6]-'0')*10 + (USART_RX_BUF[7]-'0');
				if( USART_RX_BUF[4] == '-' )
					dy = -dy;
				
				if( dx < 0 ) {
					LCD_ShowChar(50, 50, '-', 16, 0);
					LCD_ShowxNum(60,50,-dx,3,16,0);
				}
				else {
					LCD_ShowChar(50, 50, ' ', 16, 0);
					LCD_ShowxNum(60,50,dx,3,16,0);	
				}
				if( dy < 0 ) {
					LCD_ShowChar(50, 70, '-', 16, 0);
					LCD_ShowxNum(60,70,-dy,3,16,0);
				}
				else {
					LCD_ShowChar(50, 70, ' ', 16, 0);
					LCD_ShowxNum(60,70,dy,3,16,0);
				}
				
				new_direction = USART_RX_BUF[8] - '0';
				new_ring = USART_RX_BUF[9] - '0';
				
				if( new_direction != direction || new_ring != ring ) {
					LCD_Fill(50, 90, 150, 140, WHITE);
					if( new_direction != direction ) {
						switch(new_direction) {
						case 0:
							LCD_ShowString(50, 90, 200, 24, 16, "up");
						case 1:
							LCD_ShowString(50, 90, 200, 24, 16, "left_up");
						case 2:
							LCD_ShowString(50, 90, 200, 24, 16, "left");
						case 3:
							LCD_ShowString(50, 90, 200, 24, 16, "left_down");
						case 4:
							LCD_ShowString(50, 90, 200, 24, 16, "down");
						case 5:
							LCD_ShowString(50, 90, 200, 24, 16, "right_down");
						case 6:
							LCD_ShowString(50, 90, 200, 24, 16, "right");
						case 7:
							LCD_ShowString(50, 90, 200, 24, 16, "right_up");
						case 9:
							LCD_ShowString(50, 90, 200, 24, 16, "heart");
						default:
							break;
						}
						direction = new_direction;
					}
					if( new_ring != ring ) {
						LCD_ShowxNum(50, 110, 10-new_ring, 1, 16, 0);
						ring = new_ring;
		
						gui_fill_circle(240,400,230,BLACK);
				
						gui_fill_circle(240,400,220,WHITE);
						gui_fill_circle(240,400,190,BLACK);
						
						gui_fill_circle(240,400,180,WHITE);
						gui_fill_circle(240,400,150,BLACK);
						
						gui_fill_circle(240,400,140,WHITE);
						gui_fill_circle(240,400,110,BLACK);
						
						gui_fill_circle(240,400,100,WHITE);
						gui_fill_circle(240,400,70,BLACK);
						
						gui_fill_circle(240,400,60,WHITE);
						gui_fill_circle(240,400,30,RED);
						gui_fill_circle(240+230*dx/radius,400+230*dy/radius,15,YELLOW);
					}
				}
			}			
			USART_RX_STA=0;
			
			
		}
		if(dx>radius/12&&PB5>12600)PB5-=2;
		delay_ms(20);
		if(dx<-1*radius/12&&PB5>12600)PB5+=2;
		delay_ms(20);
		if(dy>radius/12&&PA8>360  )PA8-=2;       //纯负反馈式
		delay_ms(20);
		if(dy<-1*radius/12&&PA8<1800 )PA8+=2;
		delay_ms(20);
	}
//		if(dx>0&&PB5>12600)PB5-=dx*px;
//		if(dx<0&&PB5>12600)PB5-=dx*px;
//		if(dy>0&&PA8>360  )PA8-=dy*py;    //只用了P
//		if(dy<0&&PA8<1800 )PA8-=dy*py;		
//	  delay_ms(50);
		
		
		while(PA1)
		{
		while(KEY0==0)		//左转
		   {
				 if(PB5<14040)PB5+=5;
				 delay_ms(100);
			 };
		 while(KEY1==0)	//低头
          {
				 if(PA8<1800)PA8+=5;
				 delay_ms(100);
			 };			 
			 	 					
   	     while(KEY2==0)		//右转
			 {
			   if(PB5>12600)PB5-=5;
				 delay_ms(100);
			 };
			 	  
         while(WK_UP==1)//抬头
             {
				 if(PA8>360)PA8-=5; 
				 delay_ms(100);
			 };	
		 }
//	LCD_ShowChar(50,90,'B', 16, 0);
//    LCD_ShowxNum(60,90,PB5,16,16,0);
//    LCD_ShowChar(50,110,'A', 16, 0);
//	LCD_ShowxNum(60,110,PA8,16,16,0);

	}
}
