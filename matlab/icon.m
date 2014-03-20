function res = test(args)
	m=figure;
	cols = 2
	rows = 2
	for index = 1:4
	    subplot(cols, rows,index)
	    x1=0;
	    x2=4;
	    y1=0;
	    y2=4;
	    x = [x1, x2, x2, x1, x1];
	    y = [y1, y1, y2, y2, y1];
	    plot(x, y, 'b-');
	    hold on;
	    plot(2:0.01:2, 0:0.01:4, 'r');
	    plot(0:0.01:4, 2:0.01:2, 'r');
	    title('Intelligent Icon');
	    % xlim([-1, 2]);
	    % ylim([-1, 2]);
	    axes_handle = [0,1];
	    colorbar
	    colormap(cool) %will use the output colormap
	    cmap = colormap;
	    size(cmap)
	    caxis(axes_handle);
	    C1=cmap(60,:);
	    A1=[0;2;2;0];
	    B1=[2;2;4;4];
	    patch(A1,B1,C1)

	    C2=cmap(25,:);
	    A2=[2;4;4;2];
	    B2=[2;2;4;4];
	    patch(A2,B2,C2)

	    C3=cmap(19,:);
	    A3=[0;2;2;0];
	    B3=[0;0;2;2];
	    patch(A3,B3,C3)

	    C4=cmap(24,:);
	    A4=[2;2;4;4];
	    B4=[0;2;2;0];
	    patch(A4,B4,C4)
	end
	res = 1
