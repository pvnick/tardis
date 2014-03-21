function ret = show_icons(icon_data_container)
    icon_data_encoded = icon_data_container.encoded
    encoder = org.apache.commons.codec.binary.Base64;
    icon_data = eval(native2unicode(encoder.decode(unicode2native(icon_data_encoded))))
    m=figure;
    icon_count = size(icon_data, 2)
    disp(icon_count)
    cols = 4
    rows = ceil(icon_count / cols)
    for index = 1:icon_count
        icon_descriptor = icon_data(index)
        disp(strcat('making plot ', num2str(index)))

        subplot(rows, cols, index)
        x1=0;
        x2=10;
        y1=0;
        y2=10;
        x = [x1, x2, x2, x1, x1];
        y = [y1, y1, y2, y2, y1];
        
        patches = icon_descriptor.patches
        plot(x, y, 'b-');
        hold on;

        title(icon_descriptor.title);
        % xlim([-1, 2]);
        % ylim([-1, 2]);
        axes_handle = [0,1];
        colorbar
        colormap(cool) %will use the output colormap
        cmap = colormap;
        size(cmap);
        caxis(axes_handle);

        C11=cmap(patches(1),:);
        A11=[0;2.5;2.5;0];
        B11=[7.5;7.5;10;10];
        patch(A11,B11,C11)

        C12=cmap(patches(2),:);
        A12=[2.5;5;5;2.5];
        B12=[7.5;7.5;10;10];
        patch(A12,B12,C12)

        C13=cmap(patches(3),:);
        A13=[0;2.5;2.5;0];
        B13=[5;5;7.5;7.5];
        patch(A13,B13,C13)

        C14=cmap(patches(4),:);
        A14=[2.5;5;5;2.5];
        B14=[5;5;7.5;7.5];
        patch(A14,B14,C14)

        C21=cmap(patches(5),:);
        A21=[5;7.5;7.5;5];
        B21=[7.5;7.5;10;10];
        patch(A21,B21,C21)

        C22=cmap(patches(6),:);
        A22=[7.5;10;10;7.5];
        B22=[7.5;7.5;10;10];
        patch(A22,B22,C22)

        C23=cmap(patches(7),:);
        A23=[5;7.5;7.5;5];
        B23=[5;5;7.5;7.5];
        patch(A23,B23,C23)

        C24=cmap(patches(8),:);
        A24=[7.5;7.5;10;10];
        B24=[5;7.5;7.5;5];
        patch(A24,B24,C24)

        C31=cmap(patches(9),:);
        A31=[0;2.5;2.5;0];
        B31=[2.5;2.5;5;5];
        patch(A31,B31,C31)

        C32=cmap(patches(10),:);
        A32=[2.5;5;5;2.5];
        B32=[2.5;2.5;5;5];
        patch(A32,B32,C32)

        C33=cmap(patches(11),:);
        A33=[0;2.5;2.5;0];
        B33=[0;0;2.5;2.5];
        patch(A33,B33,C33)

        C34=cmap(patches(12),:);
        A34=[2.5;2.5;5;5];
        B34=[0;2.5;2.5;0];
        patch(A34,B34,C34)

        C41=cmap(patches(13),:);
        A41=[5;7.5;7.5;5];
        B41=[2.5;2.5;5;5];
        patch(A41,B41,C41)

        C42=cmap(patches(14),:);
        A42=[7.5;10;10;7.5];
        B42=[2.5;2.5;5;5];
        patch(A42,B42,C42)

        C43=cmap(patches(15),:);
        A43=[5;7.5;7.5;5];
        B43=[0;0;2.5;2.5];
        patch(A43,B43,C43)

        C44=cmap(patches(16),:);
        A44=[7.5;10;10;7.5];
        B44=[0;0;2.5;2.5];
        patch(A44,B44,C44)
    end
    ret = 1
end
